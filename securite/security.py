import socket
import threading
import time
import os
import subprocess

MAX_CONNEXIONS = 5



class GestionSecurite:
    def __init__(self):
        self.chemin_base = os.path.dirname(os.path.abspath(__file__))
        self.liste_blanche = self.charger_fichier("entreprise_ips.txt")
        self.liste_noire = self.charger_fichier("blacklist.txt")
        self.connexions_actives = 0
        self.tentatives_ip = {}

    def charger_fichier(self, nom_fichier):
        try:
            chemin_complet = os.path.join(self.chemin_base, nom_fichier)
            with open(chemin_complet, "r") as fichier:
                return set(ligne.strip() for ligne in fichier)
        except FileNotFoundError:
            return set()


    def verifier_ip(self, adresse_ip):
        if adresse_ip in self.liste_noire:
            return False
        if self.liste_blanche and adresse_ip not in self.liste_blanche:
            return False
        return True


    def autoriser_connexion(self):
        return self.connexions_actives < MAX_CONNEXIONS

    def enregistrer_connexion(self, adresse_ip):
        self.connexions_actives += 1
        self.tentatives_ip[adresse_ip] = self.tentatives_ip.get(adresse_ip, 0) + 1

    def get_mac_from_ip(self, ip):
        """Récupère l'adresse MAC d'une adresse IP via ARP"""
        try:
            # Essai 1: commande arp
            result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    # Prendre la deuxième ligne (première contient l'en-tête)
                    parts = lines[1].split()
                    # La MAC est généralement la 3e colonne
                    if len(parts) >= 3:
                        mac = parts[2]
                        # Vérifier que c'est une adresse MAC valide (format XX:XX:XX:XX:XX:XX)
                        if ':' in mac and len(mac) == 17:
                            return mac
            
            # Essai 2: commande ip neigh (Linux moderne)
            result = subprocess.run(['ip', 'neigh', 'show', ip], capture_output=True, text=True, timeout=2)
            if 'lladdr' in result.stdout:
                mac = result.stdout.split('lladdr')[1].split()[0]
                return mac
        except Exception as e:
            pass
        return "Inconnue"

    def liberer_connexion(self):
        if self.connexions_actives > 0:
            self.connexions_actives -= 1

    def enregistrerConnecter(self, adresse_ip, mac_client):
        with open(os.path.join("../serveur/logs", "connexions.log"), "a") as fichier_log:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            fichier_log.write(f"{timestamp} - Connexion de l'IP : {adresse_ip}\n")
            fichier_log.write(f"MAC Address: {mac_client}\n")

