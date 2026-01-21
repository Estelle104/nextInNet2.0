#!/bin/bash
# ============================================
# CONFIGURATION INITIALE DU POINT D'ACCÈS
# À EXÉCUTER UNE SEULE FOIS
# ============================================

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Vérification root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}✗ Lancer ce script avec sudo${NC}"
    exit 1
fi

echo -e "${BLUE}=== CONFIGURATION INITIALE AP ===${NC}"

echo -e "${YELLOW}Interfaces réseau disponibles :${NC}"
ls /sys/class/net | nl
echo ""

read -p "Interface WiFi (ex: wlo1) : " WIFI_IFACE
read -p "Interface Internet (ex: enp3s0 / eth0) : " WAN_IFACE

# Vérification des interfaces
for iface in "$WIFI_IFACE" "$WAN_IFACE"; do
    if ! ip link show "$iface" >/dev/null 2>&1; then
        echo -e "${RED}✗ Interface introuvable : $iface${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✓ Interfaces valides${NC}"

# Vérification dépendances (SANS installer)
echo -e "${YELLOW}Vérification des dépendances...${NC}"
for cmd in hostapd ip iptables; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo -e "${RED}✗ Commande manquante : $cmd${NC}"
        echo -e "${YELLOW}→ Installer manuellement : sudo apt install $cmd${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✓ Dépendances présentes${NC}"

# Activer le forwarding (persistant)
echo -e "${YELLOW}Activation du forwarding IPv4...${NC}"
sysctl -w net.ipv4.ip_forward=1 >/dev/null
sed -i 's/^#\?net.ipv4.ip_forward=.*/net.ipv4.ip_forward=1/' /etc/sysctl.conf

# Créer la configuration hostapd
CONF_DIR="/etc/hostapd"
mkdir -p "$CONF_DIR"

HOSTAPD_CONF="$CONF_DIR/hostapd_${WIFI_IFACE}.conf"

cat > "$HOSTAPD_CONF" <<EOF
interface=$WIFI_IFACE
driver=nl80211
ssid=NextInNet-Secure
hw_mode=g
channel=6
wmm_enabled=1
auth_algs=1
wpa=2
wpa_passphrase=SecureNetwork123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
EOF

echo -e "${GREEN}✓ Fichier hostapd créé : $HOSTAPD_CONF${NC}"

# Sauvegarde configuration pour le script de démarrage
echo "$WIFI_IFACE $WAN_IFACE" > /etc/nextinnet.conf

echo -e "${GREEN}=== CONFIGURATION TERMINÉE ===${NC}"
echo "Lance ensuite : sudo ./start_system.sh"
