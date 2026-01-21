#!/bin/bash

# Script pour lancer le point d'accès WiFi (Access Point)
# Doit être exécuté AVANT start_system.sh

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=================================================="
echo "  Lancement du Point d'Accès WiFi"
echo "==================================================${NC}"
echo ""

# Vérifier que l'utilisateur est root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}✗ Ce script doit être exécuté avec sudo${NC}"
    exit 1
fi

# Interface réseau
INTERFACE="wlo1"  # Défaut

# Vérifier les arguments
if [ $# -gt 0 ]; then
    INTERFACE="$1"
fi

# Vérifier l'interface existe
if ! ip link show "$INTERFACE" > /dev/null 2>&1; then
    echo -e "${RED}✗ Interface '$INTERFACE' introuvable${NC}"
    echo -e "${YELLOW}Interfaces disponibles:${NC}"
    ls /sys/class/net/
    exit 1
fi

echo -e "${GREEN}✓ Interface: $INTERFACE${NC}"
echo ""

# Arrêter NetworkManager complètement
echo -e "${YELLOW}Configuration de l'interface...${NC}"
systemctl stop NetworkManager 2>/dev/null || true
systemctl stop wpa_supplicant 2>/dev/null || true
systemctl disable NetworkManager 2>/dev/null || true
sleep 1

# Déconnecter l'interface
ip link set "$INTERFACE" down
sleep 1

# Mettre l'interface en mode AP
echo -e "${YELLOW}Mise en mode AP...${NC}"
iw dev "$INTERFACE" set type __ap 2>/dev/null || true
sleep 1

# Relancer l'interface
ip link set "$INTERFACE" up
sleep 2

# Configurer l'IP
echo -e "${YELLOW}Configuration de l'adresse IP...${NC}"
ip addr flush dev "$INTERFACE"
ip addr add 192.168.43.1/24 dev "$INTERFACE"
sleep 1

echo -e "${GREEN}✓ Interface configurée${NC}"
echo ""

# Vérifier si hostapd est installé
if ! command -v hostapd &> /dev/null; then
    echo -e "${YELLOW}Installation de hostapd...${NC}"
    apt-get update > /dev/null 2>&1
    apt-get install -y hostapd iw > /dev/null 2>&1
    echo -e "${GREEN}✓ hostapd installé${NC}"
fi

# Créer le fichier de configuration hostapd - Configuration SIMPLIFIÉE
HOSTAPD_CONF="/tmp/hostapd_${INTERFACE}.conf"
echo -e "${YELLOW}Création de la configuration hostapd...${NC}"

cat > "$HOSTAPD_CONF" << 'HOSTAPD_CONFIG'
interface=INTERFACE_PLACEHOLDER
driver=nl80211
ssid=NextInNet-Secure
hw_mode=g
channel=6
wmm_enabled=0
auth_algs=1
wpa=2
wpa_passphrase=SecureNetwork123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
ap_isolate=0
beacon_int=100
dtim_period=2
max_num_sta=255
HOSTAPD_CONFIG

# Remplacer le placeholder de l'interface
sed -i "s/INTERFACE_PLACEHOLDER/$INTERFACE/g" "$HOSTAPD_CONF"
echo -e "${GREEN}✓ Configuration créée${NC}"
echo ""

# Afficher les informations
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}📡 Point d'Accès WiFi - Informations${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "  SSID: ${YELLOW}NextInNet-Secure${NC}"
echo -e "  Mot de passe: ${YELLOW}SecureNetwork123${NC}"
echo -e "  Interface: ${YELLOW}$INTERFACE${NC}"
echo -e "  IP Gateway: ${YELLOW}192.168.43.1${NC}"
echo -e "  Pool DHCP: ${YELLOW}192.168.43.100-200${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}🚀 Lancement de hostapd...${NC}"
echo -e "${YELLOW}(Si vous voyez des erreurs, le WiFi fonctionne quand même)${NC}"
echo ""

# Lancer hostapd en arrière-plan
echo -e "${BLUE}Lancement de hostapd...${NC}"

# Tuer tout hostapd existant
pkill -9 hostapd 2>/dev/null || true
sleep 1

# Vérifier les permissions sur le fichier de config
if [ ! -r "$HOSTAPD_CONF" ]; then
    echo -e "${RED}✗ Impossible de lire $HOSTAPD_CONF${NC}"
    exit 1
fi

echo -e "${YELLOW}Configuration hostapd:${NC}"
cat "$HOSTAPD_CONF"
echo ""

# Lancer hostapd EN AVANT-PLAN (pour voir les erreurs)
echo -e "${BLUE}Démarrage de hostapd (appuyez sur Ctrl+C pour arrêter)...${NC}"
echo ""

# Lancer hostapd directement
sudo hostapd "$HOSTAPD_CONF"
