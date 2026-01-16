import socket
import threading
import os
import sys

# Ajouter le répertoire parent au chemin
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from securite.security import GestionSecurite
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5050

def main():
    security = GestionSecurite()

    print("Démarrage du serveur de logs...")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))

    server_socket.listen(5)

    print(f"Serveur en écoute sur le port {PORT}...")

    while True:
        client_socket, client_address = server_socket.accept()
        ip_client = client_address[0]  # Extraire juste l'IP du tuple

        if(ip_client and security.get_mac_from_ip(ip_client)):
            security.enregistrerConnecter(ip_client,security.get_mac_from_ip(ip_client))

        if security.verifier_ip(ip_client):
            mac_client = security.get_mac_from_ip(ip_client)
            

            print(f"[+] Client connecté : {client_address[0]}:{client_address[1]}")
            if mac_client:
                print(f"    MAC Address: {mac_client}")
            security.enregistrer_connexion(ip_client)
        else:
            print(f"[-] Connexion refusée pour l'IP : {client_address[0]}")
            client_socket.close()
        
            

if __name__ == "__main__":
    main()
