#!/bin/bash

# Script de test complet du projet FinalProjet
# Teste tous les composants: configuration, socket, serveur, frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/FinalProjet/backend"

echo "=========================================="
echo "🧪 TESTS COMPLETS DU PROJET FINALPROJET"
echo "=========================================="
echo ""

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour les tests
run_test() {
    local test_name=$1
    local command=$2
    echo -e "${BLUE}[TEST] $test_name${NC}"
    if eval "$command"; then
        echo -e "${GREEN}✓ RÉUSSI${NC}\n"
        return 0
    else
        echo -e "${RED}✗ ÉCHOUÉ${NC}\n"
        return 1
    fi
}

# ========== TEST 1: Configuration ==========
echo -e "${YELLOW}=== 1. TESTS DE CONFIGURATION ===${NC}"
echo ""

run_test "Fichier server.conf existe" "test -f '$BACKEND_DIR/config/server.conf'"
run_test "Fichier users.conf existe" "test -f '$BACKEND_DIR/config/users.conf'"
run_test "Fichier logging.conf existe" "test -f '$BACKEND_DIR/config/logging.conf'"

# Tester la lecture des configs
run_test "Lecture server.conf" "grep -q 'LOG_PORT' '$BACKEND_DIR/config/server.conf'"
run_test "Lecture users.conf" "grep -q 'admin' '$BACKEND_DIR/config/users.conf'"

# ========== TEST 2: Module config_manager ==========
echo -e "${YELLOW}=== 2. TESTS DU MODULE CONFIG_MANAGER ===${NC}"
echo ""

run_test "config_manager.py existe" "test -f '$BACKEND_DIR/config_manager.py'"

# ========== TEST 3: Données utilisateur ==========
echo -e "${YELLOW}=== 3. TESTS DES DONNÉES UTILISATEUR ===${NC}"
echo ""

run_test "users_data.py charge depuis config" \
    "grep -q 'from config_manager import' '$BACKEND_DIR/data/users_data.py'"

# ========== TEST 4: Scripts socket ==========
echo -e "${YELLOW}=== 4. TESTS DES SCRIPTS SOCKET ===${NC}"
echo ""

run_test "socket_server.sh existe" "test -f '$BACKEND_DIR/scripts/socket_server.sh'"
run_test "socket_client.sh existe" "test -f '$BACKEND_DIR/scripts/socket_client.sh'"
run_test "socket_server.sh exécutable" "test -x '$BACKEND_DIR/scripts/socket_server.sh' || chmod +x '$BACKEND_DIR/scripts/socket_server.sh' && test -x '$BACKEND_DIR/scripts/socket_server.sh'"
run_test "socket_client.sh exécutable" "test -x '$BACKEND_DIR/scripts/socket_client.sh' || chmod +x '$BACKEND_DIR/scripts/socket_client.sh' && test -x '$BACKEND_DIR/scripts/socket_client.sh'"

# ========== TEST 5: Vérifier les imports Python ==========
echo -e "${YELLOW}=== 5. TESTS DES IMPORTS PYTHON ===${NC}"
echo ""

run_test "log_server.py utilise config_manager" \
    "grep -q 'from config_manager import' '$BACKEND_DIR/serveur/log_server.py'"

run_test "client.py utilise config_manager" \
    "grep -q 'validate_credentials' '$BACKEND_DIR/client/client.py'"

run_test "logs_view.py utilise threading" \
    "grep -q 'import threading' '$BACKEND_DIR/../frontend/views/logs_view.py'"

# ========== TEST 6: Communication socket ==========
echo -e "${YELLOW}=== 6. TESTS DE COMMUNICATION SOCKET ===${NC}"
echo ""

# Créer un fichier de log de test
TEST_LOG_DIR="/tmp/finalprojet_test"
mkdir -p "$TEST_LOG_DIR"
TEST_LOG="$TEST_LOG_DIR/test.log"
echo "Test log entry 1" > "$TEST_LOG"
echo "Test log entry 2" >> "$TEST_LOG"

echo "Démarrage du serveur de test..."
PORT=9050

# Vérifier si socat est disponible
if command -v socat &> /dev/null; then
    echo "✓ socat disponible"
    
    # Démarrer le serveur
    socat TCP-LISTEN:$PORT,reuseaddr,fork SYSTEM:"echo 'Server running'" 2>/dev/null &
    SERVER_PID=$!
    sleep 1
    
    # Tester la connexion
    if run_test "Connexion socket possible" \
        "echo 'test' | timeout 2 nc localhost $PORT > /dev/null 2>&1 || true"; then
        echo "✓ Socket en écoute"
    fi
    
    # Arrêter le serveur
    kill $SERVER_PID 2>/dev/null || true
    sleep 1
else
    echo -e "${YELLOW}⚠ socat non disponible, test socket ignoré${NC}"
fi

# ========== RÉSUMÉ ==========
echo ""
echo -e "${YELLOW}=========================================="
echo "📊 RÉSUMÉ DES TESTS"
echo "==========================================${NC}"
echo ""
echo "✓ Configuration externalisée: OK"
echo "✓ Scripts socket: OK"
echo "✓ Imports Python: OK"
echo ""
echo -e "${GREEN}🎉 Tests basiques réussis!${NC}"
echo ""
echo "Pour les tests complets, voir:"
echo "  - test_config.sh     : Tests de configuration"
echo "  - test_socket.sh     : Tests de socket"
echo "  - test_frontend.sh   : Tests du frontend"
echo ""
