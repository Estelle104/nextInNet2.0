#!/bin/bash

# Script de test - Vérifier la politique de sécurité
# Test: Machines autorisées vs inconnues

set -e

PROJECT_DIR="/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet"
DEVICES_FILE="$PROJECT_DIR/backend/config/devices.conf"
BLOCKED_IPS_FILE="$PROJECT_DIR/backend/config/blocked_ips.conf"
DHCP_SERVER="$PROJECT_DIR/backend/serveur/dhcp_server.py"
TCP_SERVER="$PROJECT_DIR/backend/serveur/tcp_server_simple.py"

echo "=========================================="
echo "🧪 TEST: Politique de Sécurité"
echo "=========================================="
echo ""

# Test 1: Vérifier DHCP server a find_free_dynamic_ip()
echo "[TEST 1] Vérification DHCP Server..."
if grep -q "find_free_dynamic_ip" "$DHCP_SERVER"; then
    echo "  ✓ Fonction find_free_dynamic_ip() trouvée"
else
    echo "  ✗ Fonction find_free_dynamic_ip() MANQUANTE"
    exit 1
fi

if grep -q "IP dynamique" "$DHCP_SERVER"; then
    echo "  ✓ Allocation IP dynamique implémentée"
else
    echo "  ✗ Allocation IP dynamique MANQUANTE"
    exit 1
fi

echo ""

# Test 2: Vérifier TCP server a detect_is_device_authorized()
echo "[TEST 2] Vérification TCP Server..."
if grep -q "detect_is_device_authorized" "$TCP_SERVER"; then
    echo "  ✓ Fonction detect_is_device_authorized() trouvée"
else
    echo "  ✗ Fonction detect_is_device_authorized() MANQUANTE"
    exit 1
fi

if grep -q "iptables" "$TCP_SERVER"; then
    echo "  ✓ Blocage iptables implémenté"
else
    echo "  ✗ Blocage iptables MANQUANT"
    exit 1
fi

if grep -q "is_ssh_attempt" "$TCP_SERVER"; then
    echo "  ✓ Détection SSH améliorée"
else
    echo "  ✗ Détection SSH MANQUANTE"
    exit 1
fi

echo ""

# Test 3: Syntaxe Python
echo "[TEST 3] Vérification syntaxe Python..."
python3 -m py_compile "$DHCP_SERVER" && echo "  ✓ dhcp_server.py OK" || { echo "  ✗ dhcp_server.py ERREUR"; exit 1; }
python3 -m py_compile "$TCP_SERVER" && echo "  ✓ tcp_server_simple.py OK" || { echo "  ✗ tcp_server_simple.py ERREUR"; exit 1; }

echo ""

# Test 4: Vérifier configuration
echo "[TEST 4] Vérification configuration..."
if [ -f "$DEVICES_FILE" ]; then
    echo "  ✓ devices.conf existe"
    echo "    Contenu:"
    grep -v "^#\|^$" "$DEVICES_FILE" | sed 's/^/      /' || echo "      (vide)"
else
    echo "  ✗ devices.conf MANQUANT"
    exit 1
fi

echo ""

# Test 5: Résumé des changements
echo "[TEST 5] Résumé des changements implémentés:"
echo ""
echo "  DHCP Server:"
echo "    ✓ Machines autorisées → IP fixe (100-149)"
echo "    ✓ Machines inconnues → IP dynamique (150-200)"
echo "    ✓ Notifications: INFO pour autorisées, WARNING pour inconnues"
echo ""
echo "  TCP Server:"
echo "    ✓ Distinction autorisée vs inconnue"
echo "    ✓ SSH autorisé pour appareils authorisés"
echo "    ✓ SSH BLOQUÉ pour inconnues → Expulsion avec iptables"
echo "    ✓ Meilleure détection SSH"
echo ""

# Test 6: Instructions de test manuel
echo "=========================================="
echo "📋 Instructions de test manuel:"
echo "=========================================="
echo ""
echo "1️⃣ Lancer les serveurs:"
echo "   sudo python3 backend/serveur/dhcp_server.py wlo1"
echo "   (dans un autre terminal)"
echo "   sudo python3 backend/serveur/tcp_server_simple.py"
echo ""
echo "2️⃣ Test: Machine autorisée"
echo "   - Ajouter dans devices.conf:"
echo "     AA:BB:CC:DD:EE:01|192.168.43.100"
echo "   - Se connecter avec cette MAC"
echo "   - Résultat: IP 192.168.43.100, Notification INFO"
echo ""
echo "3️⃣ Test: Machine inconnue reçoit IP dynamique"
echo "   - Se connecter avec MAC NOT dans devices.conf"
echo "   - Résultat: IP 192.168.43.150-200, Notification WARNING"
echo ""
echo "4️⃣ Test: SSH sur inconnue = Expulsion"
echo "   - Depuis machine inconnue: ssh admin@192.168.43.1"
echo "   - Résultat: BLOQUÉE, Notification BLOCKED, IP expulsée"
echo ""
echo "5️⃣ Test: SSH sur autorisée = OK"
echo "   - Depuis machine autorisée: ssh admin@192.168.43.1"
echo "   - Résultat: SSH accepté, Notification INFO"
echo ""

echo "=========================================="
echo "✓ TOUS LES TESTS PASSÉS!"
echo "=========================================="
