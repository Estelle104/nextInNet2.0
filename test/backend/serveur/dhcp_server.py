import socket
import os

POOL = [f"192.168.1.{i}" for i in range(10, 100)]
BASE = os.path.join(os.path.dirname(__file__), "base.txt")
UDP_PORT = 6767


def load():
    data = {}
    try:
        with open(BASE) as f:
            for l in f:
                parts = l.strip().split("||")
                if len(parts) != 2:
                    continue
                m, ip = parts
                data[m] = ip
    except FileNotFoundError:
        pass
    return data


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", UDP_PORT))

print(f"DHCP simulé démarré (UDP {UDP_PORT})")

while True:
    mac, addr = sock.recvfrom(1024)
    mac = mac.decode()
    data = load()

    if mac not in data:
        if len(data) < len(POOL):
            data[mac] = POOL[len(data)]
        else:
            data[mac] = "0.0.0.0"
        with open(BASE, "w") as f:
            for m, ip in data.items():
                f.write(f"{m}||{ip}\n")

    sock.sendto(data[mac].encode(), addr)
