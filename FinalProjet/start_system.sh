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

# Déterminer le répertoire courant du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECTDIR="$SCRIPT_DIR"
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

# Configuration IP de l'AP
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

# Attendre que DHCP soit prêt
sleep 2

# Lancer TCP
echo -e "${YELLOW}Lancement TCP...${NC}"
sudo python3 serveur/tcp_server_simple.py > logs/tcp.log 2>&1 &
TCP_PID=$!

# Attendre que TCP soit prêt
sleep 2

# Lancer hostapd en arrière-plan
echo -e "${YELLOW}Lancement du WiFi AP...${NC}"
hostapd "$HOSTAPD_CONF" > logs/hostapd.log 2>&1 &
HOSTAPD_PID=$!

# Attendre que hostapd soit prêt
sleep 3

# Nettoyage à l'arrêt
trap "
echo '';
echo 'Arrêt du système...';
kill \$DHCP_PID \$TCP_PID \$HOSTAPD_PID 2>/dev/null || true;
pkill hostapd 2>/dev/null || true;
iptables -F;
iptables -t nat -F;
systemctl start NetworkManager;
exit 0
" INT TERM

# Afficher l'état du système
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ SYSTÈME DÉMARRÉ AVEC SUCCÈS${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}📡 WiFi AP : ${YELLOW}NextInNet-Secure${NC}"
echo -e "${GREEN}🔒 Mot de passe : ${YELLOW}SecureNetwork123${NC}"
echo -e "${GREEN}🌐 IP du serveur : ${YELLOW}192.168.43.1${NC}"
echo -e "${GREEN}⚙️  DHCP en cours (PID: $DHCP_PID)${NC}"
echo -e "${GREEN}🔗 TCP Serveur (PID: $TCP_PID)${NC}"
echo -e "${GREEN}📡 hostapd (PID: $HOSTAPD_PID)${NC}"
echo ""
echo -e "${YELLOW}Démarrage du client GUI...${NC}"
echo ""

# Lancer le client GUI
cd "$PROJECTDIR"
python3 backend/client/client.py

# Attendre que l'utilisateur ferme l'interface
echo -e "${YELLOW}Client GUI fermé. Arrêt du système...${NC}"
kill $DHCP_PID $TCP_PID $HOSTAPD_PID 2>/dev/null || true
pkill hostapd 2>/dev/null || true
