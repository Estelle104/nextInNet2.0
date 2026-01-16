import socket

SERVER_IP = "127.0.0.1"  # IP du serveur
PORT = 5000

os_name = platform.system()  # Windows / Linux
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((SERVER_IP, PORT))

    client.send(os_name.encode())
    reponse = client.recv(1024).decode()
    print("Réponse du serveur :", reponse)

except ConnectionRefusedError:
    print("❌ Impossible de se connecter au serveur")

finally:
    client.close()
