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
LEASE_TIME = 3600  # 1 heure

# Interface réseau (peut être modifiée par argument)
NETWORK_INTERFACE = os.environ.get('NETWORK_INTERFACE', 'wlo1')

# Fichiers
DEVICES_FILE = "/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/config/devices.conf"
DHCP_LEASES_FILE = "/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/config/dhcp_leases.conf"
DHCP_LOG_FILE = "/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/logs/dhcp.log"

# Pool d'IPs
IP_POOL_START = 100
IP_POOL_END = 200
allocated_ips = {}  # {MAC: {"ip": "...", "expiration": datetime}}
blocked_macs = set()


def load_authorized_devices():
    """Charge les appareils autorisés (MAC -> nom)"""
    authorized = {}
    try:
        if os.path.exists(DEVICES_FILE):
            with open(DEVICES_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('|')
                        if len(parts) >= 2:
                            mac = parts[0].strip().upper()
                            name = parts[1].strip() if len(parts) > 2 else "Unknown"
                            authorized[mac] = name
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


def get_ip_for_mac(mac):
    """
    Retourne l'IP assignée pour une MAC
    Accepte TOUS les appareils (machines autorisées et inconnues)
    """
    global allocated_ips
    mac_upper = mac.upper()
    
    # Vérifier si MAC bloquée
    if mac_upper in blocked_macs:
        return None
    
    # Charger les leases
    leases = load_leases()
    
    # Si lease existant valide
    if mac_upper in leases:
        if leases[mac_upper]["expiration"] > datetime.now():
            allocated_ips[mac_upper] = leases[mac_upper]
            return leases[mac_upper]["ip"]
    
    # Trouver une IP libre dans le pool
    for i in range(IP_POOL_START, IP_POOL_END + 1):
        ip = f"192.168.43.{i}"
        if not any(lease["ip"] == ip for lease in allocated_ips.values() if lease["expiration"] > datetime.now()):
            expiration = datetime.now() + timedelta(seconds=LEASE_TIME)
            allocated_ips[mac_upper] = {"ip": ip, "expiration": expiration}
            save_lease(mac_upper, ip, expiration)
            
            # Vérifier si autorisée pour le message
            devices = load_authorized_devices()
            if mac_upper in devices:
                log(f"✓ IP assignée (AUTORISÉE): {mac} -> {ip} ({devices[mac_upper]})")
            else:
                log(f"⚠️ IP assignée (INCONNUE): {mac} -> {ip}")
            return ip
    
    log(f"✗ Pool d'IP épuisé pour {mac}")
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


def build_dhcp_offer(transaction_id, client_mac, offered_ip):
    """Construit une réponse DHCP OFFER"""
    packet = bytearray(300)
    
    # Header DHCP
    packet[0] = 2  # DHCP OFFER (bootreply)
    packet[1] = 1  # Ethernet
    packet[2] = 6  # Hardware address length
    packet[3] = 0  # Hops
    packet[4:8] = transaction_id
    packet[8:10] = b'\x00\x00'  # Seconds
    packet[10:12] = b'\x00\x00'  # Flags
    packet[12:16] = b'\x00\x00\x00\x00'  # Client IP
    packet[16:20] = format_ip(offered_ip)  # Your IP
    packet[20:24] = format_ip(DHCP_SERVER_IP)  # Server IP
    packet[24:28] = b'\x00\x00\x00\x00'  # Gateway
    packet[28:28+6] = bytes.fromhex(client_mac.replace(':', ''))  # Client MAC
    
    # Magic cookie
    magic_cookie_pos = 236
    packet[magic_cookie_pos:magic_cookie_pos+4] = b'\x63\x82\x53\x63'
    
    # Options DHCP
    options_pos = magic_cookie_pos + 4
    options = bytearray()
    
    # Option 53: DHCP Message Type (OFFER=2)
    options += bytes([53, 1, DHCP_OFFER])
    
    # Option 1: Subnet Mask
    options += bytes([1, 4]) + format_ip(SUBNET_MASK)
    
    # Option 3: Router (Gateway)
    options += bytes([3, 4]) + format_ip(GATEWAY)
    
    # Option 6: DNS
    options += bytes([6, 4]) + format_ip(DNS)
    
    # Option 51: Lease Time
    lease_bytes = struct.pack('!I', LEASE_TIME)
    options += bytes([51, 4]) + lease_bytes
    
    # Option 54: DHCP Server
    options += bytes([54, 4]) + format_ip(DHCP_SERVER_IP)
    
    # Option 255: End
    options += bytes([255])
    
    packet[options_pos:options_pos+len(options)] = options
    
    return bytes(packet[:options_pos+len(options)])


def build_dhcp_ack(transaction_id, client_mac, assigned_ip):
    """Construit une réponse DHCP ACK"""
    packet = bytearray(300)
    
    # Header DHCP
    packet[0] = 2  # DHCP ACK (bootreply)
    packet[1] = 1  # Ethernet
    packet[2] = 6  # Hardware address length
    packet[3] = 0  # Hops
    packet[4:8] = transaction_id
    packet[8:10] = b'\x00\x00'  # Seconds
    packet[10:12] = b'\x00\x00'  # Flags
    packet[12:16] = b'\x00\x00\x00\x00'  # Client IP
    packet[16:20] = format_ip(assigned_ip)  # Your IP
    packet[20:24] = format_ip(DHCP_SERVER_IP)  # Server IP
    packet[24:28] = b'\x00\x00\x00\x00'  # Gateway
    packet[28:28+6] = bytes.fromhex(client_mac.replace(':', ''))  # Client MAC
    
    # Magic cookie
    magic_cookie_pos = 236
    packet[magic_cookie_pos:magic_cookie_pos+4] = b'\x63\x82\x53\x63'
    
    # Options DHCP
    options_pos = magic_cookie_pos + 4
    options = bytearray()
    
    # Option 53: DHCP Message Type (ACK=5)
    options += bytes([53, 1, DHCP_ACK])
    
    # Option 1: Subnet Mask
    options += bytes([1, 4]) + format_ip(SUBNET_MASK)
    
    # Option 3: Router (Gateway)
    options += bytes([3, 4]) + format_ip(GATEWAY)
    
    # Option 6: DNS
    options += bytes([6, 4]) + format_ip(DNS)
    
    # Option 51: Lease Time
    lease_bytes = struct.pack('!I', LEASE_TIME)
    options += bytes([51, 4]) + lease_bytes
    
    # Option 54: DHCP Server
    options += bytes([54, 4]) + format_ip(DHCP_SERVER_IP)
    
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
        
        # Vérifier si MAC autorisée
        authorized = load_authorized_devices()
        if client_mac not in authorized:
            log(f"✗ MAC non autorisée: {client_mac}")
            return
        
        # Assigner une IP
        offered_ip = get_ip_for_mac(client_mac)
        if not offered_ip:
            log(f"✗ Impossible d'assigner IP pour {client_mac}")
            return
        
        # Envoyer DHCP OFFER
        offer = build_dhcp_offer(transaction_id, client_mac, offered_ip)
        sock.sendto(offer, (client_addr[0], DHCP_CLIENT_PORT))
        
        log(f"✓ DHCP OFFER envoyé: {client_mac} -> {offered_ip}")
        
        # Attendre et traiter REQUEST (dans un vrai serveur DHCP)
        # Pour cet implémentation simple, on envoie directement ACK
        time.sleep(0.1)
        
        ack = build_dhcp_ack(transaction_id, client_mac, offered_ip)
        sock.sendto(ack, (client_addr[0], DHCP_CLIENT_PORT))
        
        log(f"✓ DHCP ACK envoyé: {client_mac} -> {offered_ip}")
        
    except Exception as e:
        log(f"✗ Erreur traitement DHCP: {e}")


def start_dhcp_server():
    """Démarre le serveur DHCP"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind le socket à l'interface réseau spécifiée
        try:
            if hasattr(socket, 'SO_BINDTODEVICE'):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, 
                               NETWORK_INTERFACE.encode() + b'\0')
        except (OSError, AttributeError) as e:
            log(f"⚠️ Attention: Impossible de binder à l'interface {NETWORK_INTERFACE}: {e}")
        
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
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
