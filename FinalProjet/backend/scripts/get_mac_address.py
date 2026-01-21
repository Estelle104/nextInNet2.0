#!/usr/bin/env python3
"""
Utilitaire pour obtenir l'adresse MAC de la machine
"""

import socket
import struct
import fcntl
import os

def get_mac_address(interface="eth0"):
    """Retourne l'adresse MAC d'une interface réseau"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', interface.encode('utf-8')[:15]))
        mac = ''.join('%02x:' % b for b in info[18:24])[:-1]
        return mac.upper()
    except Exception as e:
        return None

def get_interfaces():
    """Liste les interfaces réseau disponibles"""
    interfaces = []
    for if_name in os.listdir('/sys/class/net/'):
        try:
            mac = get_mac_address(if_name)
            if mac:
                interfaces.append((if_name, mac))
        except:
            pass
    return interfaces

if __name__ == "__main__":
    print("=== Adresses MAC des interfaces réseau ===\n")
    
    interfaces = get_interfaces()
    for if_name, mac in interfaces:
        print(f"{if_name}: {mac}")
    
    if interfaces:
        print(f"\nInterface par défaut (eth0 ou wlan0):")
        for if_name, mac in interfaces:
            if if_name in ["eth0", "wlan0"]:
                print(f"  → {if_name}: {mac}")
                break
