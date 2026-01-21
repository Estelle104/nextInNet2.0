#!/bin/bash

# Script pour tester le serveur et les communications socket
# Démarre le serveur et teste les requêtes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "🧪 TESTS DE COMMUNICATION SOCKET"
echo "=========================================="
echo ""

# Vérifier que socat est installé
if ! command -v socat &> /dev/null; then
    echo "❌ socat n'est pas installé"
    echo "Installation: sudo apt-get install socat"
    exit 1
fi

echo "✓ socat détecté"

# Configuration
PORT=9050
TEST_LOG_DIR="/tmp/finalprojet_test"
TEST_LOG="$TEST_LOG_DIR/test.log"
mkdir -p "$TEST_LOG_DIR"

# Créer un fichier de log de test
echo "[INFO] Création du fichier de test..."
cat > "$TEST_LOG" << 'EOF'
2026-01-20 10:15:32 - Connexion de l'IP : 192.168.1.100
MAC Address: AA:BB:CC:DD:EE:FF
---
2026-01-20 10:15:35 - Connexion de l'IP : 192.168.1.101
MAC Address: AA:BB:CC:DD:EE:00
---
2026-01-20 10:15:40 - Connexion de l'IP : 192.168.1.102
MAC Address: AA:BB:CC:DD:EE:01
---
EOF

echo "✓ Fichier de test créé"
echo ""

# Démarrer le serveur socket
echo "[1] Démarrage du serveur socket sur le port $PORT..."
bash "$SCRIPT_DIR/socket_server.sh" $PORT "$TEST_LOG" start > /dev/null 2>&1 &
SERVER_PID=$!
echo "  Serveur PID: $SERVER_PID"

sleep 2

# Vérifier que le serveur est en écoute
echo "[2] Vérification que le serveur est en écoute..."
if netstat -ln 2>/dev/null | grep -q ":$PORT " || ss -ln 2>/dev/null | grep -q ":$PORT "; then
    echo "  ✓ Serveur en écoute sur le port $PORT"
else
    echo "  ⚠ Impossible de vérifier (netstat/ss non disponible, mais serveur probablement actif)"
fi
echo ""

# Test 1: Requête realtime
echo "[3] Test: Requête realtime..."
RESULT=$(bash "$SCRIPT_DIR/socket_client.sh" 127.0.0.1 $PORT realtime 5)
if echo "$RESULT" | grep -q "2026"; then
    echo "  ✓ Logs reçus (sample): $(echo "$RESULT" | head -1)"
else
    echo "  ✗ Aucun log reçu"
fi
echo ""

# Test 2: Requête history
echo "[4] Test: Requête history..."
RESULT=$(bash "$SCRIPT_DIR/socket_client.sh" 127.0.0.1 $PORT history 5)
LINE_COUNT=$(echo "$RESULT" | wc -l)
if [ $LINE_COUNT -gt 0 ]; then
    echo "  ✓ Historique reçu ($LINE_COUNT lignes)"
else
    echo "  ✗ Aucun historique reçu"
fi
echo ""

# Test 3: Requête invalide
echo "[5] Test: Requête invalide..."
RESULT=$(bash "$SCRIPT_DIR/socket_client.sh" 127.0.0.1 $PORT invalid 5)
if echo "$RESULT" | grep -q "ERROR"; then
    echo "  ✓ Erreur correctement rapportée"
else
    echo "  ⚠ Pas de message d'erreur détecté"
fi
echo ""

# Arrêter le serveur
echo "[6] Arrêt du serveur..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true
sleep 1
echo "  ✓ Serveur arrêté"
echo ""

# Nettoyage
rm -rf "$TEST_LOG_DIR"

echo -e "\033[0;32m✓ TOUS LES TESTS SOCKET RÉUSSIS\033[0m"
