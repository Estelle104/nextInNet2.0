import socket
import os
from datetime import datetime

LOG_PORT = 5050
LOG_FILE = os.path.join(os.path.dirname(__file__), "Connexion.log")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", LOG_PORT))
sock.listen(5)

print(f"Serveur de logs démarré (TCP {LOG_PORT})")

def get_logs(log_type):
    try:
        with open(LOG_FILE, "r") as f:
            logs = f.readlines()
        if log_type == "realtime":
            return logs[-10:]  # Return the last 10 logs for real-time logs
        elif log_type == "history":
            return logs  # Return all logs for history
        else:
            return ["[ERROR] Type de log inconnu."]
    except FileNotFoundError:
        return ["[ERROR] Fichier de log introuvable."]

while True:
    c, a = sock.accept()
    try:
        msg = c.recv(1024).decode().strip()  # Receive the log type (e.g., 'realtime' or 'history')
        logs = get_logs(msg)  # Fetch the appropriate logs
        response = "\n".join(logs)  # Join logs into a single string
        c.sendall(response.encode())  # Send the logs back to the client
    except Exception as e:
        error_message = f"[ERROR] {e}"
        c.sendall(error_message.encode())
    finally:
        c.close()
