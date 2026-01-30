#!/usr/bin/env python3
"""
Serveur de Logs Simplifié - Port 5050
Enregistre les connexions et renvoie les logs demandés
SÉCURITÉ: Détection des machines inconnues (IP/MAC non enregistrées)
"""

import socket
import threading
import os
import time
import subprocess
from datetime import datetime
from collections import defaultdict

PORT = 5050
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "logs", "Connexion.log")
DEVICES_FILE = os.path.join(BASE_DIR, "config", "devices.conf")
NOTIFICATIONS_FILE = os.path.join(BASE_DIR, "logs", "notifications.log")
BLOCKED_IPS_FILE = os.path.join(BASE_DIR, "config", "blocked_ips.conf")

# Créer les répertoires et fichiers essentiels au démarrage
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(DEVICES_FILE), exist_ok=True)
for f in [LOG_FILE, NOTIFICATIONS_FILE]:
    if not os.path.exists(f):
        try:
            open(f, 'a').close()
        except:
            pass

# Lock global pour éviter les race conditions lors d'accès fichier
_file_lock = threading.Lock()

# Tracking des connexions inconnues (IP -> timestamp de connexion)
unknown_connections = {}
blocked_ips = set()
TIMEOUT_UNKNOWN = 15  # 15 secondes avant d'expulser du réseau

def load_devices():
    """Charge la liste des appareils autorisés depuis devices.conf (MAC -> IP)"""
    devices = {}
    try:
        with _file_lock:
            if os.path.exists(DEVICES_FILE):
                with open(DEVICES_FILE, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split('|')
                            if len(parts) >= 2:
                                mac = parts[0].strip().upper()
                                ip = parts[1].strip()
                                devices[mac] = ip  # MAC -> IP mapping
    except Exception as e:
        print(f"✗ Erreur chargement devices: {e}")
    return devices

def load_blocked_ips():
    """Charge la liste des IPs bloquées"""
    blocked = set()
    try:
        with _file_lock:
            if os.path.exists(BLOCKED_IPS_FILE):
                with open(BLOCKED_IPS_FILE, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            blocked.add(line)
    except Exception as e:
        print(f"✗ Erreur chargement blocked IPs: {e}")
    return blocked

def is_device_known(ip, mac=None):
    """Vérifie si la combinaison MAC|IP est enregistrée"""
    devices = load_devices()
    
    # Si MAC fournie, vérifier que MAC -> IP correspond
    if mac:
        mac_upper = mac.upper()
        if mac_upper in devices:
            expected_ip = devices[mac_upper]
            if expected_ip == ip:
                return True
            else:
                # MAC connue mais IP différente (peut être due au DHCP)
                print(f"⚠️ MAC {mac} reconnue mais IP mismatch: attendu {expected_ip}, reçu {ip}")
                return False
        return False
    
    # Si pas de MAC, vérifier juste l'IP (compatibilité rétroactive)
    return any(ip == expected_ip for expected_ip in devices.values())

def ping_and_shutdown(ip):
    """
    Ping une machine et l'éteint avec 'shutdown -h now'
    Utilisé pour les machines inconnues qui tentent SSH
    """
    try:
        # Vérifier que la machine est accessible (ping)
        ping_result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", ip],
            capture_output=True,
            timeout=3
        )
        
        if ping_result.returncode == 0:
            # Machine accessible - l'éteindre
            print(f"🔴 PING OK pour {ip} - Envoi du signal d'extinction...")
            log_to_file(f"🔴 PING OK {ip} - Envoi shutdown -h now", "CRITICAL")
            
            # Essayer d'envoyer la commande shutdown via SSH ou directement
            # Essayer d'abord avec SSH root
            try:
                shutdown_result = subprocess.run(
                    ["ssh", "-o", "ConnectTimeout=2", "-o", "StrictHostKeyChecking=no", 
                     f"root@{ip}", "shutdown -h now"],
                    capture_output=True,
                    timeout=3
                )
                if shutdown_result.returncode == 0:
                    print(f"✓ Commande shutdown envoyée via SSH à {ip}")
                    log_to_file(f"✓ Shutdown SSH envoyé à {ip}", "CRITICAL")
                else:
                    print(f"⚠️ SSH échoué, tentative alternative...")
            except:
                print(f"⚠️ SSH non disponible, tentative avec sudo...")
                # Tentative alternative si SSH échoue
                try:
                    subprocess.run(
                        ["sudo", "systemctl", "poweroff", "--no-block"],
                        capture_output=True,
                        timeout=2
                    )
                except:
                    pass
        else:
            # Machine non accessible
            print(f"⚠️ PING ÉCHOUÉ pour {ip}")
            log_to_file(f"⚠️ PING échoué {ip} - Machine non accessible", "WARNING")
    
    except Exception as e:
        print(f"✗ Erreur ping/shutdown: {e}")
        log_to_file(f"✗ Erreur ping/shutdown {ip}: {e}", "ERROR")

def block_ip(ip):
    """Ajoute une IP à la liste des bloquées et bloque avec iptables"""
    global blocked_ips
    blocked_ips.add(ip)
    try:
        with _file_lock:
            with open(BLOCKED_IPS_FILE, 'a') as f:
                f.write(f"{ip}\n")
        print(f"✓ IP {ip} ajoutée à blocked_ips.conf")
    except Exception as e:
        print(f"✗ Erreur blocage IP: {e}")
    
    # ✅ NOUVEAU: Bloquer avec iptables (expulsion réelle du réseau)
    try:
        # Bloquer les entrées (INPUT)
        subprocess.run(
            ["sudo", "iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"],
            check=False,
            capture_output=True,
            timeout=3
        )
        # Bloquer le forwarding (FORWARD)
        subprocess.run(
            ["sudo", "iptables", "-I", "FORWARD", "-s", ip, "-j", "DROP"],
            check=False,
            capture_output=True,
            timeout=3
        )
        print(f"✓ iptables: IP {ip} bloquée (expulsion réseau)")
    except Exception as e:
        print(f"⚠️ iptables non disponible ou erreur: {e}")

def detect_is_device_authorized(ip):
    """Vérifie si l'IP est autorisée (dans devices.conf)"""
    devices = load_devices()
    authorized_ips = set(devices.values())
    return ip in authorized_ips

def create_notification(notification_type, message):
    """Crée une notification (WARNING, BLOCKED, etc)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(NOTIFICATIONS_FILE), exist_ok=True)
    try:
        with _file_lock:
            with open(NOTIFICATIONS_FILE, 'a') as f:
                f.write(f"[{timestamp}] [{notification_type}] {message}\n")
        print(f"⚠️ NOTIFICATION [{notification_type}]: {message}")
    except Exception as e:
        print(f"✗ Erreur notification: {e}")

def ensure_log_file():
    """Crée le dossier et fichier de logs s'ils n'existent pas"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'a').close()

def log_to_file(message, level="INFO"):
    """Enregistre un message dans le fichier de log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with _file_lock:
            with open(LOG_FILE, 'a') as f:
                f.write(f"[{timestamp}] [{level}] {message}\n")
        print(f"✓ Log: [{level}] {message}")
    except Exception as e:
        print(f"✗ Erreur écriture: {e}")

def get_logs_from_file(log_type, limit=10):
    """Récupère les logs du fichier"""
    try:
        with _file_lock:
            if not os.path.exists(LOG_FILE):
                return "[INFO] Aucun log disponible\n"
            
            with open(LOG_FILE, 'r') as f:
                logs = f.readlines()
        
        if log_type == "realtime":
            logs_to_send = logs[-limit:]
        elif log_type == "history":
            logs_to_send = logs
        else:
            logs_to_send = logs[-limit:]
        
        return "".join(logs_to_send) if logs_to_send else "[INFO] Aucun log\n"
    except Exception as e:
        return f"[ERROR] {e}\n"

def check_and_handle_unknown(ip, port, request):
    """
    Vérifie si la machine est autorisée ou inconnue et applique les règles:
    - AUTORISÉE (dans devices.conf) → SSH OK, juste log
    - INCONNUE (IP dynamique 150-200) → SSH = BLOQUÉE + EXPULSÉE
    - BLOQUÉE (dans blocked_ips.conf) → Refusée
    """
    is_local = ip == "127.0.0.1" or ip == "localhost"
    
    if is_local:
        return ("AUTHORIZED", 0)
    
    # Vérifier si IP est bloquée
    blocked_ips_list = load_blocked_ips()
    if ip in blocked_ips_list:
        log_to_file(f"SSH refusée - IP bloquée {ip}:{port}", "INFO")
        create_notification("BLOCKED", f"🚫 IP bloquée {ip} refusée")
        return ("BLOCKED", 0)
    
    # Vérifier si c'est une machine AUTORISÉE (dans devices.conf)
    is_authorized = detect_is_device_authorized(ip)
    
    if is_authorized:
        # ✅ Machine autorisée
        # SSH est OK, juste enregistrer
        if "ssh" in request.lower() or port == 22 or request.startswith("22"):
            log_to_file(f"✓ SSH accepté depuis machine autorisée: {ip}:{port}", "INFO")
            create_notification("INFO", f"✓ SSH autorisé depuis {ip} (machine connue)")
        else:
            log_to_file(f"✓ Connexion établie - Machine autorisée: {ip}:{port}", "INFO")
        
        # Réinitialiser tracking inconnue si présente
        if ip in unknown_connections:
            del unknown_connections[ip]
        
        return ("AUTHORIZED", 0)
    
    # ❌ Machine INCONNUE (IP dynamique 150-200)
    else:
        if ip not in unknown_connections:
            # Première connexion de cette IP inconnue
            unknown_connections[ip] = time.time()
            log_to_file(f"⚠️ MACHINE INCONNUE DÉTECTÉE: {ip}:{port} (15s avant expulsion)", "WARNING")
            create_notification("WARNING", f"⚠️ MACHINE INCONNUE DÉTECTÉE: {ip}:{port}")
        
        # ✅ NOUVEAU: Détecter SSH sur inconnue = BLOQUER + EXPULSER + PING + SHUTDOWN
        is_ssh_attempt = (
            "ssh" in request.lower() or 
            port == 22 or 
            request.startswith("22") or
            "SSH" in request or
            "OpenSSH" in request
        )
        
        if is_ssh_attempt:
            log_to_file(f"🚫 TENTATIVE SSH MACHINE INCONNUE BLOQUÉE: {ip}:{port} - EXPULSÉE!", "ERROR")
            create_notification("BLOCKED", f"🚫 TENTATIVE SSH MACHINE INCONNUE: {ip} - BLOQUÉE & EXPULSÉE!")
            
            # ✅ NOUVEAU: Ping + Shutdown
            print(f"🔴 ALERTE SSH: Ping et extinction de {ip}...")
            ping_and_shutdown(ip)  # Lance ping et shutdown
            
            # Bloquer l'IP
            block_ip(ip)
            
            return ("BLOCKED", 0)
        
        # Calculer le temps restant avant timeout (15s pour inconnues)
        time_since_connection = time.time() - unknown_connections[ip]
        time_remaining = TIMEOUT_UNKNOWN - time_since_connection
        
        if time_remaining <= 0:
            log_to_file(f"MACHINE INCONNUE EXPULSÉE - Timeout: {ip}:{port}", "WARNING")
            create_notification("TIMEOUT", f"⏱️ EXPULSION: Machine inconnue {ip} expulsée après 15s (timeout)")
            
            # Bloquer avec iptables
            block_ip(ip)
            if ip in unknown_connections:
                del unknown_connections[ip]
            return ("TIMEOUT", 0)
        
        # Machine inconnue acceptée (temporairement), mais tracking actif
        return ("UNKNOWN", time_remaining)


def handle_client(client_socket, client_address):
    """Traite chaque client qui se connecte"""
    try:
        ip = client_address[0]
        port = client_address[1]
        
        # Recevoir la demande
        try:
            request = client_socket.recv(1024).decode().strip()
        except:
            request = ""
        
        # Vérifier les règles de sécurité
        status, time_remaining = check_and_handle_unknown(ip, port, request)
        
        # Traiter selon le status
        if status == "BLOCKED":
            log_to_file(f"Connexion refusée - Machine bloquée: {ip}:{port}", "ERROR")
            client_socket.send("[ERROR] Acces refuse - Machine bloquee\n".encode('utf-8'))
            client_socket.close()
            return
        
        elif status == "TIMEOUT":
            log_to_file(f"Connexion expirée - Timeout: {ip}:{port}", "WARNING")
            client_socket.send("[ERROR] Timeout - Connexion expiree (1 minute)\n".encode('utf-8'))
            client_socket.close()
            return
        
        elif status == "UNKNOWN":
            # Machine inconnue - accepter (IP dynamique) mais afficher le temps restant avant expulsion
            is_local = ip == "127.0.0.1" or ip == "localhost"
            if not is_local:
                log_to_file(f"[UNKNOWN] Machine inconnue (IP dynamique) - {int(time_remaining)}s avant expulsion: {ip}:{port}", "WARNING")
        
        # ✅ ENREGISTRER la connexion (même locale)
        is_local = ip == "127.0.0.1" or ip == "localhost"
        
        if not is_local:
            log_to_file(f"Connexion établie: {ip}:{port}", "INFO")
            print(f"[REMOTE CONNECTION] {ip}:{port}")
        else:
            log_to_file(f"Connexion locale: {ip}:{port}", "INFO")
        
        if not is_local:
            print(f"Request from {ip}: {request}")
        
        # Traiter la demande
        if request.startswith("realtime"):
            parts = request.split()
            limit = int(parts[1]) if len(parts) > 1 else 10
            response = get_logs_from_file("realtime", limit)
        elif request.startswith("history"):
            response = get_logs_from_file("history")
        else:
            response = "[INFO] Commandes: realtime [N] | history\n"
        
        # Envoyer la réponse
        client_socket.sendall(response.encode())
        
        if not is_local:
            print(f"✓ Réponse envoyée à {ip}")
        
    except Exception as e:
        print(f"✗ Erreur client: {e}")
        ip = client_address[0] if client_address else "unknown"
        log_to_file(f"Erreur connexion: {ip} - {str(e)[:50]}", "ERROR")
    finally:
        client_socket.close()

def monitor_unknown_connections():
    """Thread de surveillance - expulse les machines inconnues après 15s"""
    while True:
        try:
            time.sleep(1)  # Vérifier toutes les 1 seconde
            current_time = time.time()
            ips_to_remove = []
            
            for ip, connection_time in list(unknown_connections.items()):
                elapsed = current_time - connection_time
                
                if elapsed >= TIMEOUT_UNKNOWN:
                    # Vérifier que l'IP n'est pas déjà bloquée
                    if ip not in load_blocked_ips():
                        # Temps écoulé - expulser
                        print(f"🚫 MACHINE INCONNUE EXPULSÉE - Timeout 15s: {ip}")
                        log_to_file(f"🚫 MACHINE INCONNUE EXPULSÉE - Timeout 15s: {ip}", "WARNING")
                        create_notification("TIMEOUT", f"⏱️ EXPULSION: Machine inconnue {ip} expulsée après 15s")
                        
                        # Bloquer avec iptables et ajouter à blocked_ips.conf
                        block_ip(ip)
                    
                    ips_to_remove.append(ip)
            
            # Nettoyer les IPs expulsées
            for ip in ips_to_remove:
                if ip in unknown_connections:
                    del unknown_connections[ip]
        
        except Exception as e:
            print(f"✗ Erreur monitoring: {e}")

def start_server():
    """Démarre le serveur TCP"""
    ensure_log_file()
    
    # Ajouter des logs d'initialisation
    log_to_file("Serveur démarré")
    
    # ✅ NOUVEAU: Lancer le thread de surveillance des machines inconnues
    monitor_thread = threading.Thread(target=monitor_unknown_connections, daemon=True)
    monitor_thread.start()
    print(f"✓ Thread de surveillance des connexions inconnues lancé")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(("0.0.0.0", PORT))
        server.listen(5)
        print(f"✓ Serveur démarré sur 0.0.0.0:{PORT}")
        print(f"✓ Logs: {LOG_FILE}")
        log_to_file("Serveur prêt à accepter les connexions")
        
        while True:
            try:
                client_socket, client_address = server.accept()
                # Traiter dans un thread séparé
                thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                thread.start()
            except KeyboardInterrupt:
                print("\n✓ Arrêt du serveur...")
                log_to_file("Serveur arrêté")
                break
            except Exception as e:
                print(f"✗ Erreur: {e}")
                continue
    
    except Exception as e:
        print(f"✗ Erreur serveur: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
