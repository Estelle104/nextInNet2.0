import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.client.login import check_login
from backend.client.network import request_ip, send_log
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_FILE = os.path.join(BASE_DIR, "serveur", "base.txt")
LOG_FILE = os.path.join(BASE_DIR, "serveur", "Connexion.log")
MAC = "AA:BB:CC:DD:EE:01"


def authenticate(username, password):
    """Authenticate user and return success/failure."""
    return check_login(username, password)


def get_client_ip():
    """Request an IP address from DHCP server for this client's MAC."""
    return request_ip(MAC)


def log_action(action, status="OK"):
    """Send a log message to the log server."""
    msg = f"{MAC}||{action}||{status}"
    send_log(msg)


if __name__ == '__main__':
    print("Client module loaded. Use authenticate(), get_client_ip(), log_action() functions.")


#if __name__ == "__main__":
#    print("Lancement de l'interface client...")
#    start_ui()
