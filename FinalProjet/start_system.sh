#!/bin/bash
# ============================================
# DÉMARRAGE DU SYSTÈME COMPLET
# ============================================

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECTDIR="/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet"
BACKEND="$PROJECTDIR/backend"

# Vérification configuration
if [ ! -f /etc/nextinnet.conf ]; then
    echo -e "${RED}✗ CONFIGURE_AP.sh non exécuté${NC}"
    exit 1
fi

read WIFI_IFACE WAN_IFACE < /etc/nextinnet.conf
HOSTAPD_CONF="/etc/hostapd/hostapd_${WIFI_IFACE}.conf"

echo -e "${BLUE}=== DÉMARRAGE SYSTÈME RÉSEAU ===${NC}"

# Arrêt TEMPORAIRE des services conflictuels
echo -e "${YELLOW}Arrêt temporaire NetworkManager et wpa_supplicant...${NC}"
systemctl stop NetworkManager || true
systemctl stop wpa_supplicant || true

# Configuration IP de l’AP
echo -e "${YELLOW}Configuration IP sur $WIFI_IFACE...${NC}"
ip link set "$WIFI_IFACE" down || true
ip addr flush dev "$WIFI_IFACE"
ip addr add 192.168.43.1/24 dev "$WIFI_IFACE"
ip link set "$WIFI_IFACE" up

# Nettoyage iptables
iptables -F
iptables -t nat -F

# Configuration NAT
echo -e "${YELLOW}Configuration NAT...${NC}"
iptables -t nat -A POSTROUTING -o "$WAN_IFACE" -j MASQUERADE
iptables -A FORWARD -i "$WIFI_IFACE" -o "$WAN_IFACE" -j ACCEPT
iptables -A FORWARD -i "$WAN_IFACE" -o "$WIFI_IFACE" -m state --state ESTABLISHED,RELATED -j ACCEPT

# Lancer DHCP Python
echo -e "${YELLOW}Lancement DHCP...${NC}"
mkdir -p "$BACKEND/logs"
cd "$BACKEND"
sudo python3 serveur/dhcp_server.py "$WIFI_IFACE" > logs/dhcp.log 2>&1 &
DHCP_PID=$!

# Lancer TCP
echo -e "${YELLOW}Lancement TCP...${NC}"
python3 serveur/tcp_server_simple.py > logs/tcp.log 2>&1 &
TCP_PID=$!

# Nettoyage à l’arrêt
trap "
echo '';
echo 'Arrêt du système...';
kill $DHCP_PID $TCP_PID 2>/dev/null;
pkill hostapd 2>/dev/null;
iptables -F;
iptables -t nat -F;
systemctl start NetworkManager;
exit 0
" INT TERM

# Lancer hostapd en avant-plan
echo -e "${GREEN}📡 WiFi AP lancé : NextInNet-Secure${NC}"
echo -e "${GREEN}🔒 Mot de passe : SecureNetwork123${NC}"
echo ""
hostapd "$HOSTAPD_CONF"
