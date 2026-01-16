import socket
import os
from datetime import datetime

LOG_PORT = 5050
LOG_FILE = os.path.join(os.path.dirname(__file__), "Connexion.log")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", LOG_PORT))
sock.listen(5)

print(f"Serveur de logs démarré (TCP {LOG_PORT})")

while True:
    c, a = sock.accept()
    try:
        msg = c.recv(1024).decode()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(LOG_FILE, "a") as f:
            f.write(f"{now}||{msg}\n")
    except Exception:
        pass
    finally:
        c.close()
