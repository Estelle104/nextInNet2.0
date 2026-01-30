#!/usr/bin/env python3
"""
Serveur DHCP Simplifié
IPs fixes pour MAC autorisées
IPs dynamiques temporaires pour inconnues
"""

import socket
import struct
import threading
import os
import sys
import time
from datetime import datetime, timedelta

# =====================================================
# CHEMINS
# =====================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
LOG_DIR = os.path.join(BASE_DIR, "logs")

DHCP_CONF_FILE = os.path.join(CONFIG_DIR, "dhcp.conf")
DEVICES_FILE = os.path.join(CONFIG_DIR, "devices.conf")
LEASES_FILE = os.path.join(CONFIG_DIR, "dhcp_leases.conf")
DHCP_LOG_FILE = os.path.join(LOG_DIR, "dhcp.log")

os.makedirs(LOG_DIR, exist_ok=True)

# =====================================================
# CHARGEMENT CONFIG
# =====================================================

def load_dhcp_config():
    cfg = {}
    with open(DHCP_CONF_FILE) as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                cfg[k.strip()] = v.strip()
    return cfg

CFG = load_dhcp_config()

NETWORK = CFG["NETWORK"]
NETMASK = CFG["NETMASK"]
GATEWAY = CFG["GATEWAY"]
SERVER_IP = CFG["SERVER_IP"]
DNS = CFG["DNS"]

POOL_START = int(CFG["POOL_START"])
POOL_END = int(CFG["POOL_END"])
DYN_START = int(CFG["DYNAMIC_START"])
DYN_END = int(CFG["DYNAMIC_END"])

LEASE_AUTH = int(CFG["LEASE_AUTHORIZED"])
LEASE_UNKNOWN = int(CFG["LEASE_UNKNOWN"])

NETWORK_INTERFACE = os.environ.get("NETWORK_INTERFACE", "wlan0")

# =====================================================
# CONSTANTES DHCP
# =====================================================

DHCP_SERVER_PORT = 67
DHCP_CLIENT_PORT = 68

DHCP_OFFER = 2
DHCP_ACK = 5

allocated_ips = {}

# =====================================================
# LOG
# =====================================================

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(DHCP_LOG_FILE, "a") as f:
        f.write(line + "\n")

# =====================================================
# CONFIG DEVICES
# =====================================================

def load_authorized_devices():
    devices = {}
    if os.path.exists(DEVICES_FILE):
        with open(DEVICES_FILE) as f:
            for line in f:
                if "|" in line:
                    mac, ip = line.strip().split("|")
                    devices[mac.upper()] = ip
    return devices

def load_leases():
    leases = {}
    if os.path.exists(LEASES_FILE):
        with open(LEASES_FILE) as f:
            for line in f:
                if "|" in line:
                    mac, ip, exp = line.strip().split("|")
                    exp = datetime.fromisoformat(exp)
                    if exp > datetime.now():
                        leases[mac] = {"ip": ip, "expiration": exp}
    return leases

def save_lease(mac, ip, expiration):
    with open(LEASES_FILE, "a") as f:
        f.write(f"{mac}|{ip}|{expiration.isoformat()}\n")

# =====================================================
# IP MANAGEMENT
# =====================================================

def find_free_dynamic_ip():
    used = {
        int(v["ip"].split(".")[3])
        for v in allocated_ips.values()
        if v["expiration"] > datetime.now()
    }
    base = NETWORK.rsplit(".", 1)[0]
    for i in range(DYN_START, DYN_END + 1):
        if i not in used:
            return f"{base}.{i}"
    return None

def get_ip_for_mac(mac):
    mac = mac.upper()
    leases = load_leases()
    auth = load_authorized_devices()

    if mac in leases:
        allocated_ips[mac] = leases[mac]
        return leases[mac]["ip"], LEASE_AUTH if mac in auth else LEASE_UNKNOWN

    if mac in auth:
        ip = auth[mac]
        exp = datetime.now() + timedelta(seconds=LEASE_AUTH)
        allocated_ips[mac] = {"ip": ip, "expiration": exp}
        save_lease(mac, ip, exp)
        return ip, LEASE_AUTH

    ip = find_free_dynamic_ip()
    if not ip:
        return None, None

    exp = datetime.now() + timedelta(seconds=LEASE_UNKNOWN)
    allocated_ips[mac] = {"ip": ip, "expiration": exp}
    save_lease(mac, ip, exp)
    return ip, LEASE_UNKNOWN

# =====================================================
# DHCP PACKETS
# =====================================================

def format_ip(ip):
    return bytes(int(x) for x in ip.split("."))

def parse_mac(data):
    return ":".join(f"{b:02X}" for b in data[:6])

def build_packet(msg_type, xid, mac, ip, lease):
    pkt = bytearray(300)
    pkt[0] = 2
    pkt[1] = 1
    pkt[2] = 6
    pkt[4:8] = xid
    pkt[10:12] = b"\x80\x00"
    pkt[16:20] = format_ip(ip)
    pkt[20:24] = format_ip(SERVER_IP)
    pkt[28:34] = bytes.fromhex(mac.replace(":", ""))
    pkt[236:240] = b"\x63\x82\x53\x63"

    opts = bytearray()
    opts += bytes([53, 1, msg_type])
    opts += bytes([1, 4]) + format_ip(NETMASK)
    opts += bytes([3, 4]) + format_ip(GATEWAY)
    opts += bytes([6, 4]) + format_ip(DNS)
    opts += bytes([51, 4]) + struct.pack("!I", lease)
    opts += bytes([54, 4]) + format_ip(SERVER_IP)
    opts += bytes([255])

    pkt[240:240+len(opts)] = opts
    return pkt[:240+len(opts)]

# =====================================================
# HANDLER
# =====================================================

def handle_dhcp(data, sock):
    xid = data[4:8]
    mac = parse_mac(data[28:34])

    log(f"DISCOVER {mac}")

    ip, lease = get_ip_for_mac(mac)
    if not ip:
        log(f"REFUS {mac}", "ERROR")
        return

    offer = build_packet(DHCP_OFFER, xid, mac, ip, lease)
    sock.sendto(offer, ("255.255.255.255", DHCP_CLIENT_PORT))

    time.sleep(0.1)

    ack = build_packet(DHCP_ACK, xid, mac, ip, lease)
    sock.sendto(ack, ("255.255.255.255", DHCP_CLIENT_PORT))

    log(f"ACK {mac} → {ip} ({lease}s)", "DHCP")

# =====================================================
# SERVER
# =====================================================

def start():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if hasattr(socket, "SO_BINDTODEVICE"):
        sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_BINDTODEVICE,
            NETWORK_INTERFACE.encode() + b"\0"
        )

    sock.bind(("0.0.0.0", DHCP_SERVER_PORT))
    log(f"DHCP démarré sur {NETWORK_INTERFACE}", "START")

    try:
        while True:
            data, _ = sock.recvfrom(1024)
            threading.Thread(
                target=handle_dhcp,
                args=(data, sock),
                daemon=True
            ).start()
    except KeyboardInterrupt:
        log("DHCP arrêté", "STOP")

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    if not os.path.exists(DHCP_CONF_FILE):
        print("❌ dhcp.conf manquant")
        sys.exit(1)

    start()
