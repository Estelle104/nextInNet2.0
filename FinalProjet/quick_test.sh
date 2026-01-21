#!/bin/bash

# Quick test - Teste le tout en quelques secondes
# Usage: bash quick_test.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo "🚀 QUICK TEST - Test rapide du projet"
echo "======================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS++)) || true
}

test_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL++)) || true
}

# Test 1: Fichiers
echo "📁 Vérification des fichiers..."
[ -f "$BACKEND_DIR/config/server.conf" ] && test_pass "server.conf" || test_fail "server.conf"
[ -f "$BACKEND_DIR/config/users.conf" ] && test_pass "users.conf" || test_fail "users.conf"
[ -f "$BACKEND_DIR/config/logging.conf" ] && test_pass "logging.conf" || test_fail "logging.conf"
[ -f "$BACKEND_DIR/config_manager.py" ] && test_pass "config_manager.py" || test_fail "config_manager.py"
echo ""

# Test 2: Python imports
echo "🐍 Vérification des imports Python..."
IMPORT_OUT=$(python3 << EOF
import sys
sys.path.insert(0, "$BACKEND_DIR")

try:
    from config_manager import validate_credentials, get_log_port
    print("import_ok")
except Exception as e:
    print(f"import_failed:{e}")
EOF
)

if echo "$IMPORT_OUT" | grep -q "import_ok"; then
    test_pass "config_manager importable"
else
    test_fail "config_manager importable"
fi

# Test 3: Configuration
echo ""
echo "⚙️  Vérification de la configuration..."
CONFIG_OUT=$(python3 << EOF
import sys
sys.path.insert(0, "$BACKEND_DIR")

try:
    from config_manager import validate_credentials, get_log_port, get_users
    
    # Test credentials
    if validate_credentials("admin", "admin123"):
        print("credentials_ok")
    else:
        print("credentials_fail")
    
    # Test config
    port = get_log_port()
    if port == 5050:
        print("port_ok")
    else:
        print(f"port_fail:{port}")
        
    users = get_users()
    if len(users) >= 4:
        print("users_ok")
    else:
        print(f"users_fail:{len(users)}")
        
except Exception as e:
    print(f"error:{e}")
EOF
)

echo "$CONFIG_OUT" | while IFS= read -r line; do
    if [[ "$line" == "credentials_ok" ]]; then
        test_pass "Credentials"
    elif [[ "$line" == "port_ok" ]]; then
        test_pass "Port configuration"
    elif [[ "$line" == "users_ok" ]]; then
        test_pass "Users loaded"
    fi
done

echo ""
echo "📊 RÉSUMÉ"
echo "=========="
echo -e "Réussis: ${GREEN}$PASS${NC}"
echo -e "Échoués: ${RED}$FAIL${NC}"

if [ $FAIL -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ TOUS LES TESTS RAPIDES RÉUSSIS!${NC}"
    echo ""
    echo "Prochaines étapes:"
    echo "  1. Démarrer le serveur:"
    echo "     python3 FinalProjet/backend/serveur/log_server.py"
    echo ""
    echo "  2. Dans un autre terminal, lancer le client:"
    echo "     python3 FinalProjet/backend/client/client.py"
    echo ""
    echo "  3. Se connecter avec: admin / admin123"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}❌ Certains tests ont échoué${NC}"
    echo "Consultez le GUIDE_TEST.md pour plus d'infos"
    exit 1
fi
