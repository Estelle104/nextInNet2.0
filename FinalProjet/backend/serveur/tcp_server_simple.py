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
from datetime import datetime
from collections import defaultdict

PORT = 5050
LOG_FILE = "/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/logs/Connexion.log"
DEVICES_FILE = "/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/config/devices.conf"
NOTIFICATIONS_FILE = "/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/logs/notifications.log"
BLOCKED_IPS_FILE = "/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/config/blocked_ips.conf"

# Tracking des connexions inconnues (IP -> timestamp de connexion)
unknown_connections = {}
blocked_ips = set()
TIMEOUT_UNKNOWN = 30  # 30 secondes avant de couper la connexion

def load_devices():
    """Charge la liste des appareils autorisés depuis devices.conf (MAC -> IP)"""
    devices = {}
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
                            devices[mac] = ip  # MAC -> IP mapping
    except Exception as e:
        print(f"✗ Erreur chargement devices: {e}")
    return devices

def load_blocked_ips():
    """Charge la liste des IPs bloquées"""
    blocked = set()
    try:
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

def block_ip(ip):
    """Ajoute une IP à la liste des bloquées"""
    global blocked_ips
    blocked_ips.add(ip)
    try:
        with open(BLOCKED_IPS_FILE, 'a') as f:
            f.write(f"{ip}\n")
    except Exception as e:
        print(f"✗ Erreur blocage IP: {e}")

def create_notification(notification_type, message):
    """Crée une notification (WARNING, BLOCKED, etc)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(NOTIFICATIONS_FILE), exist_ok=True)
    try:
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
        with open(LOG_FILE, 'a') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
        print(f"✓ Log: [{level}] {message}")
    except Exception as e:
        print(f"✗ Erreur écriture: {e}")

def get_logs_from_file(log_type, limit=10):
    """Récupère les logs du fichier"""
    try:
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
    """Vérifie si la machine est inconnue et applique les règles"""
    is_local = ip == "127.0.0.1" or ip == "localhost"
    
    if is_local:
        return ("AUTHORIZED", 0)  # (status, time_allowed)
    
    # Vérifier si IP est bloquée
    blocked_ips_list = load_blocked_ips()
    if ip in blocked_ips_list:
        log_to_file(f"[BLOCKED] Tentative connexion d'une IP bloquée: {ip}:{port}", "BLOCKED")
        create_notification("BLOCKED", f"IP bloquée {ip} refusée")
        return ("BLOCKED", 0)
    
    # Vérifier si c'est une machine connue
    if not is_device_known(ip):
        # Machine inconnue détectée
        if ip not in unknown_connections:
            # Première connexion de cette IP inconnue
            unknown_connections[ip] = time.time()
            log_to_file(f"[UNKNOWN] Machine INCONNUE connectée: {ip}:{port}", "UNKNOWN")
            create_notification("WARNING", f"🔴 MACHINE INCONNUE DÉTECTÉE: {ip}:{port}")
        
        # Vérifier si elle essaie SSH (port 22) ou autres tentatives suspectes
        if "ssh" in request.lower() or request.startswith("22"):
            log_to_file(f"[ATTACK] Tentative SSH/port22 depuis: {ip}:{port}", "BLOCKED")
            create_notification("BLOCKED", f"🚫 ATTAQUE SSH DEPUIS {ip} - BLOQUÉE IMMÉDIATEMENT")
            block_ip(ip)
            return ("BLOCKED", 0)
        
        # Calculer le temps restant avant timeout
        time_since_connection = time.time() - unknown_connections[ip]
        time_remaining = TIMEOUT_UNKNOWN - time_since_connection
        
        if time_remaining <= 0:
            # Timeout dépassé - déconnecter
            log_to_file(f"[TIMEOUT] Machine inconnue DÉCONNECTÉE (timeout 30s): {ip}:{port}", "UNKNOWN")
            create_notification("TIMEOUT", f"⏱️ DÉCONNEXION: Machine inconnue {ip} supprimée après 30 secondes")
            del unknown_connections[ip]
            return ("TIMEOUT", 0)
        
        # Retourner le statut UNKNOWN pour laisser se connecter mais tracker
        return ("UNKNOWN", time_remaining)
    
    # Machine connue, réinitialiser le compte
    if ip in unknown_connections:
        del unknown_connections[ip]
    
    return ("AUTHORIZED", 0)

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
            client_socket.send("[ERROR] Acces refuse - Machine bloquee\n".encode('utf-8'))
            client_socket.close()
            return
        
        elif status == "TIMEOUT":
            client_socket.send("[ERROR] Timeout - Connexion expiree (1 minute)\n".encode('utf-8'))
            client_socket.close()
            return
        
        elif status == "UNKNOWN":
            # Machine inconnue - accepter mais afficher le temps restant
            is_local = ip == "127.0.0.1" or ip == "localhost"
            log_to_file(f"[UNKNOWN] Connexion acceptée temporairement (⏱️ {int(time_remaining)}s avant déconnexion)", "UNKNOWN")
        
        # ✅ ENREGISTRER la connexion (même locale)
        is_local = ip == "127.0.0.1" or ip == "localhost"
        
        if not is_local:
            log_to_file(f"[CONNECTION] Client from {ip}:{port}", "INFO")
            print(f"[REMOTE CONNECTION] {ip}:{port}")
        else:
            log_to_file(f"[CONNECTION] Client from {ip}:{port}", "INFO")
        
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
    finally:
        client_socket.close()

def start_server():
    """Démarre le serveur TCP"""
    ensure_log_file()
    
    # Ajouter des logs d'initialisation
    log_to_file("[SERVER] Starting server...")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(("0.0.0.0", PORT))
        server.listen(5)
        print(f"✓ Serveur démarré sur 0.0.0.0:{PORT}")
        print(f"✓ Logs: {LOG_FILE}")
        log_to_file("[SERVER] Server started successfully")
        
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
                log_to_file("[SERVER] Server stopped")
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
