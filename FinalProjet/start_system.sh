#!/bin/bash
set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECTDIR="$SCRIPT_DIR"
BACKEND="$PROJECTDIR/backend"

if [ ! -f /etc/nextinnet.conf ]; then
    echo -e "${RED}✗ CONFIGURE_AP.sh non exécuté${NC}"
    exit 1
fi

read WIFI_IFACE WAN_IFACE < /etc/nextinnet.conf
HOSTAPD_CONF="/etc/hostapd/hostapd_${WIFI_IFACE}.conf"

echo -e "${BLUE}=== DÉMARRAGE SYSTÈME RÉSEAU ===${NC}"

# 🔥 COUPER LES CONFLITS
systemctl stop NetworkManager || true
systemctl stop wpa_supplicant || true
nmcli dev set "$WIFI_IFACE" managed no || true

# 🔥 RESET INTERFACE WIFI
ip link set "$WIFI_IFACE" down
iw dev "$WIFI_IFACE" set type managed
ip link set "$WIFI_IFACE" up
sleep 1

# 🔥 PASSAGE EN MODE AP
ip link set "$WIFI_IFACE" down
iw dev "$WIFI_IFACE" set type __ap
ip link set "$WIFI_IFACE" up

# 🔥 IP AP
ip addr flush dev "$WIFI_IFACE"
ip addr add 192.168.43.1/24 dev "$WIFI_IFACE"

# 🔥 NETTOYAGE IPTABLES
iptables -F
iptables -t nat -F

iptables -t nat -A POSTROUTING -o "$WAN_IFACE" -j MASQUERADE
iptables -A FORWARD -i "$WIFI_IFACE" -o "$WAN_IFACE" -j ACCEPT
iptables -A FORWARD -i "$WAN_IFACE" -o "$WIFI_IFACE" -m state --state ESTABLISHED,RELATED -j ACCEPT

# 🔥 DHCP
mkdir -p "$BACKEND/logs"
cd "$BACKEND"
python3 serveur/dhcp_server.py "$WIFI_IFACE" > logs/dhcp.log 2>&1 &
DHCP_PID=$!

sleep 2

# 🔥 TCP
python3 serveur/tcp_server_simple.py > logs/tcp.log 2>&1 &
TCP_PID=$!

sleep 2

# 🔥 HOSTAPD (CRITIQUE)
hostapd "$HOSTAPD_CONF" > logs/hostapd.log 2>&1 &
HOSTAPD_PID=$!

sleep 3

if ! ps -p $HOSTAPD_PID > /dev/null; then
    echo -e "${RED}✗ hostapd a échoué${NC}"
    exit 1
fi

# 🔥 NETTOYAGE GARANTI
cleanup() {
    echo -e "${YELLOW}Arrêt du système...${NC}"
    kill $DHCP_PID $TCP_PID $HOSTAPD_PID 2>/dev/null || true
    pkill hostapd 2>/dev/null || true
    iptables -F
    iptables -t nat -F
    nmcli dev set "$WIFI_IFACE" managed yes || true
    systemctl start NetworkManager
}

trap cleanup EXIT INT TERM

echo -e "${GREEN}✓ SYSTÈME PRÊT${NC}"

# 🔥 LANCER GUI SANS BLOQUER LE CLEANUP
cd "$PROJECTDIR"
python3 backend/client/client.py &
GUI_PID=$!
wait $GUI_PID
