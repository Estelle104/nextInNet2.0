#!/usr/bin/env python3
"""
Serveur DHCP Simplifié
Assigne des IPs basées sur les adresses MAC des clients
Maintient un registre des allocations IP/MAC
"""

import socket
import struct
import threading
import os
import sys
import time
from datetime import datetime, timedelta
from collections import defaultdict

DHCP_SERVER_PORT = 67
DHCP_CLIENT_PORT = 68
DHCP_DISCOVER = 1
DHCP_OFFER = 2
DHCP_REQUEST = 3
DHCP_ACK = 5
DHCP_NACK = 6
DHCP_RELEASE = 7

# Configuration du réseau
NETWORK_ADDRESS = "192.168.43.0"
SUBNET_MASK = "255.255.255.0"
GATEWAY = "192.168.43.1"  # Votre PC (point d'accès)
DHCP_SERVER_IP = "192.168.43.1"
DNS = "8.8.8.8"
LEASE_TIME = 3600  # 1 heure pour les machines autorisées
LEASE_TIME_UNKNOWN = 20  # 20 secondes pour les machines inconnues (un peu plus que 15s d'expulsion)

# Interface réseau (peut être modifiée par argument)
NETWORK_INTERFACE = os.environ.get('NETWORK_INTERFACE', 'wlo1')

# Fichiers
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEVICES_FILE = os.path.join(BASE_DIR, "config", "devices.conf")
DHCP_LEASES_FILE = os.path.join(BASE_DIR, "config", "dhcp_leases.conf")
DHCP_LOG_FILE = os.path.join(BASE_DIR, "logs", "dhcp.log")
NOTIFICATIONS_FILE = os.path.join(BASE_DIR, "logs", "notifications.log")

# Pool d'IPs
IP_POOL_START = 100
IP_POOL_END = 200
# Pool dynamique pour inconnues: 150-200 (durée: 15 secondes avant expulsion)
allocated_ips = {}  # {MAC: {"ip": "...", "expiration": datetime}}
blocked_macs = set()


def load_authorized_devices():
    """Charge les appareils autorisés (MAC|IP -> aucun nom)"""
    authorized = {}  # {MAC: IP}
    try:
        if os.path.exists(DEVICES_FILE):
            with open(DEVICES_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('|')
                        if len(parts) >= 2:
                            mac = parts[0].strip().upper()
                            ip = parts[1].strip()
                            authorized[mac] = ip
    except Exception as e:
        log(f"✗ Erreur chargement appareils: {e}")
    return authorized


def load_leases():
    """Charge les allocations DHCP existantes"""
    leases = {}
    try:
        if os.path.exists(DHCP_LEASES_FILE):
            with open(DHCP_LEASES_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('|')
                        if len(parts) == 3:
                            mac = parts[0].strip().upper()
                            ip = parts[1].strip()
                            expiration = datetime.fromisoformat(parts[2].strip())
                            if expiration > datetime.now():
                                leases[mac] = {"ip": ip, "expiration": expiration}
    except Exception as e:
        log(f"✗ Erreur chargement leases: {e}")
    return leases


def save_lease(mac, ip, expiration):
    """Sauvegarde une allocation DHCP"""
    os.makedirs(os.path.dirname(DHCP_LEASES_FILE), exist_ok=True)
    try:
        with open(DHCP_LEASES_FILE, 'a') as f:
            f.write(f"{mac.upper()}|{ip}|{expiration.isoformat()}\n")
        log(f"✓ Lease sauvegardé: {mac} -> {ip}")
    except Exception as e:
        log(f"✗ Erreur sauvegarde lease: {e}")


def find_free_dynamic_ip():
    """Trouve une IP libre dans le pool dynamique (150-200) pour les machines inconnues"""
    dynamic_start = 150
    dynamic_end = 200
    
    # Récupérer les IPs déjà utilisées
    used_ips = set()
    for lease in allocated_ips.values():
        if lease["expiration"] > datetime.now():
            ip_parts = lease["ip"].split('.')
            if len(ip_parts) == 4 and ip_parts[3].isdigit():
                used_ips.add(int(ip_parts[3]))
    
    # Trouver la première IP libre
    for ip_suffix in range(dynamic_start, dynamic_end + 1):
        if ip_suffix not in used_ips:
            return f"192.168.43.{ip_suffix}"
    
    return None


def get_ip_for_mac(mac):
    """
    Retourne l'IP assignée pour une MAC
    - MAC autorisée (dans devices.conf) → IP fixe
    - MAC inconnue → IP dynamique (150-200)
    """
    global allocated_ips
    mac_upper = mac.upper()
    
    # Vérifier si MAC bloquée
    if mac_upper in blocked_macs:
        return None
    
    # Charger les leases et appareils autorisés
    leases = load_leases()
    authorized_devices = load_authorized_devices()
    
    # Si lease existant valide
    if mac_upper in leases:
        if leases[mac_upper]["expiration"] > datetime.now():
            allocated_ips[mac_upper] = leases[mac_upper]
            ip = leases[mac_upper]["ip"]
            
            # Vérifier si MAC+IP sont autorisés
            is_authorized = (mac_upper in authorized_devices and 
                           authorized_devices[mac_upper] == ip)
            
            if not is_authorized:
                send_notification(mac_upper, ip, False)
                log(f"⚠️ INCONNUE: MAC={mac} IP={ip}")
            else:
                send_notification(mac_upper, ip, True)
                log(f"✓ AUTORISÉE: MAC={mac} IP={ip}")
            
            return ip
    
    # MAC autorisée - assigner l'IP fixe définie
    if mac_upper in authorized_devices:
        required_ip = authorized_devices[mac_upper]
        
        # Vérifier si cette IP est disponible
        ip_taken = any(lease["ip"] == required_ip for lease in allocated_ips.values() 
                      if lease["expiration"] > datetime.now())
        
        if not ip_taken:
            expiration = datetime.now() + timedelta(seconds=LEASE_TIME)
            allocated_ips[mac_upper] = {"ip": required_ip, "expiration": expiration}
            save_lease(mac_upper, required_ip, expiration)
            
            send_notification(mac_upper, required_ip, True)
            log(f"MAC={mac} IP={required_ip} | Status: ✓ AUTORISÉE (fixe)", "CONNEXION")
            return required_ip
        else:
            log(f"MAC={mac} IP={required_ip} | Status: ⚠️ DÉJÀ UTILISÉE", "CONNEXION")
            return None
    
    # ✅ NOUVEAU: MAC inconnue - allouer une IP dynamique (150-200)
    else:
        dynamic_ip = find_free_dynamic_ip()
        if dynamic_ip:
            # Lease court (20s) pour les inconnues qui seront expulsées à 15s
            expiration = datetime.now() + timedelta(seconds=LEASE_TIME_UNKNOWN)
            allocated_ips[mac_upper] = {"ip": dynamic_ip, "expiration": expiration}
            save_lease(mac_upper, dynamic_ip, expiration)
            
            send_notification(mac_upper, dynamic_ip, False)
            log(f"MAC={mac} IP={dynamic_ip} | Status: ⚠️ INCONNUE (IP dynamique) | Expulsion après 15s | Lease: {LEASE_TIME_UNKNOWN}s", "CONNEXION")
            return dynamic_ip
        else:
            log(f"MAC={mac} | Status: ❌ POOL PLEIN", "CONNEXION")
            return None


def format_ip(ip_string):
    """Convertit une IP string en format de 4 octets"""
    parts = ip_string.split('.')
    return bytes([int(p) for p in parts])


def format_mac(mac_bytes):
    """Convertit les bytes MAC en format string"""
    return ':'.join(f'{b:02X}' for b in mac_bytes)


def parse_mac(mac_bytes):
    """Extrait la MAC de la requête DHCP"""
    if len(mac_bytes) >= 6:
        return format_mac(mac_bytes[:6])
    return None


def log(message):
    """Enregistre un message dans le log DHCP"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(DHCP_LOG_FILE), exist_ok=True)
    message_full = f"[{timestamp}] {message}"
    print(message_full)
    try:
        with open(DHCP_LOG_FILE, 'a') as f:
            f.write(message_full + "\n")
    except:
        pass


def send_notification(mac, ip, is_authorized):
    """Envoie une notification si l'appareil est inconnue ou bloqué"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        os.makedirs(os.path.dirname(NOTIFICATIONS_FILE), exist_ok=True)
        with open(NOTIFICATIONS_FILE, 'a') as f:
            if is_authorized:
                msg = f"[{timestamp}] [INFO] ✓ Appareil autorisé: MAC={mac} IP={ip}\n"
            else:
                msg = f"[{timestamp}] [WARNING] ⚠️ Appareil inconnue: MAC={mac} IP={ip}\n"
            
            f.write(msg)
    except Exception as e:
        log(f"✗ Erreur écriture notification: {e}")


def build_dhcp_offer(transaction_id, client_mac, offered_ip, client_ip=None, lease_time=LEASE_TIME):
    """Construit une réponse DHCP OFFER"""
    packet = bytearray(300)
    
    # Header DHCP
    packet[0] = 2  # DHCP OFFER (bootreply)
    packet[1] = 1  # Ethernet
    packet[2] = 6  # Hardware address length
    packet[3] = 0  # Hops
    packet[4:8] = transaction_id
    packet[8:10] = b'\x00\x00'  # Seconds elapsed
    packet[10:12] = b'\x80\x00'  # Broadcast flag activé
    packet[12:16] = client_ip if client_ip else b'\x00\x00\x00\x00'  # ciaddr
    packet[16:20] = format_ip(offered_ip)  # yiaddr (Your IP)
    packet[20:24] = format_ip(DHCP_SERVER_IP)  # siaddr (Server IP)
    packet[24:28] = format_ip(GATEWAY)  # giaddr (Gateway/Relay)
    packet[28:34] = bytes.fromhex(client_mac.replace(':', ''))  # chaddr (Client MAC)
    packet[34:108] = b'\x00' * 74  # sname (servername) - empty
    packet[108:236] = b'\x00' * 128  # file - empty
    
    # Magic cookie (byte 236-239)
    packet[236:240] = b'\x63\x82\x53\x63'
    
    # Options DHCP
    options_pos = 240
    options = bytearray()
    
    # Option 53: DHCP Message Type (OFFER=2)
    options += bytes([53, 1, DHCP_OFFER])
    
    # Option 1: Subnet Mask
    options += bytes([1, 4]) + format_ip(SUBNET_MASK)
    
    # Option 3: Router (Gateway)
    options += bytes([3, 4]) + format_ip(GATEWAY)
    
    # Option 6: DNS Servers
    options += bytes([6, 8]) + format_ip(DNS) + format_ip("8.8.4.4")
    
    # Option 15: Domain Name
    domain = b"nextinnet.local"
    options += bytes([15, len(domain)]) + domain
    
    # Option 51: Lease Time
    lease_bytes = struct.pack('!I', lease_time)
    options += bytes([51, 4]) + lease_bytes
    
    # Option 54: DHCP Server Identifier
    options += bytes([54, 4]) + format_ip(DHCP_SERVER_IP)
    
    # Option 58: Renewal Time (T1)
    renewal_bytes = struct.pack('!I', lease_time // 2)
    options += bytes([58, 4]) + renewal_bytes
    
    # Option 59: Rebinding Time (T2)
    rebinding_bytes = struct.pack('!I', int(lease_time * 0.875))
    options += bytes([59, 4]) + rebinding_bytes
    
    # Option 255: End
    options += bytes([255])
    
    packet[options_pos:options_pos+len(options)] = options
    
    return bytes(packet[:options_pos+len(options)])


def build_dhcp_ack(transaction_id, client_mac, assigned_ip, client_ip=None, lease_time=LEASE_TIME):
    """Construit une réponse DHCP ACK"""
    packet = bytearray(300)
    
    # Header DHCP
    packet[0] = 2  # DHCP ACK (bootreply)
    packet[1] = 1  # Ethernet
    packet[2] = 6  # Hardware address length
    packet[3] = 0  # Hops
    packet[4:8] = transaction_id
    packet[8:10] = b'\x00\x00'  # Seconds elapsed
    packet[10:12] = b'\x80\x00'  # Broadcast flag activé
    packet[12:16] = client_ip if client_ip else b'\x00\x00\x00\x00'  # ciaddr
    packet[16:20] = format_ip(assigned_ip)  # yiaddr (Your IP)
    packet[20:24] = format_ip(DHCP_SERVER_IP)  # siaddr (Server IP)
    packet[24:28] = format_ip(GATEWAY)  # giaddr (Gateway/Relay)
    packet[28:34] = bytes.fromhex(client_mac.replace(':', ''))  # chaddr (Client MAC)
    packet[34:108] = b'\x00' * 74  # sname (servername) - empty
    packet[108:236] = b'\x00' * 128  # file - empty
    
    # Magic cookie (byte 236-239)
    packet[236:240] = b'\x63\x82\x53\x63'
    
    # Options DHCP
    options_pos = 240
    options = bytearray()
    
    # Option 53: DHCP Message Type (ACK=5)
    options += bytes([53, 1, DHCP_ACK])
    
    # Option 1: Subnet Mask
    options += bytes([1, 4]) + format_ip(SUBNET_MASK)
    
    # Option 3: Router (Gateway)
    options += bytes([3, 4]) + format_ip(GATEWAY)
    
    # Option 6: DNS Servers
    options += bytes([6, 8]) + format_ip(DNS) + format_ip("8.8.4.4")
    
    # Option 15: Domain Name
    domain = b"nextinnet.local"
    options += bytes([15, len(domain)]) + domain
    
    # Option 51: Lease Time
    lease_bytes = struct.pack('!I', lease_time)
    options += bytes([51, 4]) + lease_bytes
    
    # Option 54: DHCP Server Identifier
    options += bytes([54, 4]) + format_ip(DHCP_SERVER_IP)
    
    # Option 58: Renewal Time (T1)
    renewal_bytes = struct.pack('!I', lease_time // 2)
    options += bytes([58, 4]) + renewal_bytes
    
    # Option 59: Rebinding Time (T2)
    rebinding_bytes = struct.pack('!I', int(lease_time * 0.875))
    options += bytes([59, 4]) + rebinding_bytes
    
    # Option 255: End
    options += bytes([255])
    
    packet[options_pos:options_pos+len(options)] = options
    
    return bytes(packet[:options_pos+len(options)])


def handle_dhcp_request(data, client_addr, sock):
    """Traite une requête DHCP"""
    try:
        # Extraire les informations
        msg_type = data[0]  # 1=BOOTREQUEST
        client_mac = parse_mac(data[28:28+16])
        transaction_id = data[4:8]
        
        if not client_mac:
            return
        
        log(f"→ DHCP Request de {client_mac}")
        
        # Assigner une IP (accepte TOUS les clients, autorisés ou non)
        offered_ip = get_ip_for_mac(client_mac)
        if not offered_ip:
            log(f"✗ Impossible d'assigner IP pour {client_mac}")
            return
        
        # Déterminer le lease_time selon si le client est autorisé ou inconnue
        authorized_devices = load_authorized_devices()
        is_authorized = client_mac.upper() in authorized_devices
        lease_time = LEASE_TIME if is_authorized else LEASE_TIME_UNKNOWN
        
        # Envoyer DHCP OFFER en BROADCAST (255.255.255.255:68)
        # Les clients DHCP écoutent sur le broadcast avant d'avoir une IP
        offer = build_dhcp_offer(transaction_id, client_mac, offered_ip, lease_time=lease_time)
        sock.sendto(offer, ("255.255.255.255", DHCP_CLIENT_PORT))
        
        log(f"✓ DHCP OFFER envoyé (broadcast): {client_mac} -> {offered_ip} | Lease: {lease_time}s")
        
        # Attendre et traiter REQUEST (dans un vrai serveur DHCP)
        # Pour cet implémentation simple, on envoie directement ACK
        time.sleep(0.1)
        
        ack = build_dhcp_ack(transaction_id, client_mac, offered_ip, lease_time=lease_time)
        sock.sendto(ack, ("255.255.255.255", DHCP_CLIENT_PORT))
        
        log(f"✓ DHCP ACK envoyé (broadcast): {client_mac} -> {offered_ip} | Lease: {lease_time}s")
        
    except Exception as e:
        log(f"✗ Erreur traitement DHCP: {e}")


def start_dhcp_server():
    """Démarre le serveur DHCP"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Bind le socket à l'interface réseau spécifiée
        try:
            if hasattr(socket, 'SO_BINDTODEVICE'):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, 
                               NETWORK_INTERFACE.encode() + b'\0')
        except (OSError, AttributeError) as e:
            log(f"⚠️ Attention: Impossible de binder à l'interface {NETWORK_INTERFACE}: {e}")
        
        # Bind à tous les interfaces sur le port 67
        sock.bind(('0.0.0.0', DHCP_SERVER_PORT))
        
        log(f"🚀 Serveur DHCP démarré sur port {DHCP_SERVER_PORT}")
        log(f"   Interface: {NETWORK_INTERFACE}")
        log(f"   Réseau: {NETWORK_ADDRESS}/{SUBNET_MASK}")
        log(f"   Gateway: {GATEWAY}")
        log(f"   Pool: 192.168.43.{IP_POOL_START}-{IP_POOL_END}")
        
        while True:
            try:
                data, client_addr = sock.recvfrom(1024)
                if len(data) >= 240:
                    # Traiter en thread pour ne pas bloquer
                    thread = threading.Thread(
                        target=handle_dhcp_request,
                        args=(data, client_addr, sock)
                    )
                    thread.daemon = True
                    thread.start()
            except Exception as e:
                log(f"✗ Erreur réception: {e}")
                
    except Exception as e:
        log(f"✗ Erreur démarrage DHCP: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    # Vérifier les arguments
    if len(sys.argv) > 1:
        NETWORK_INTERFACE = sys.argv[1]
        log(f"Interface réseau fournie: {NETWORK_INTERFACE}")
    
    try:
        log(f"Démarrage du serveur DHCP sur l'interface: {NETWORK_INTERFACE}")
        start_dhcp_server()
    except KeyboardInterrupt:
        log("\n⏹️ Serveur DHCP arrêté")
