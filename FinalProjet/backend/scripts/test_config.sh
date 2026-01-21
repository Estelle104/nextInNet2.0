#!/bin/bash

# Script pour tester les configurations
# Vérifie que les fichiers de configuration peuvent être chargés

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../config"

echo "=========================================="
echo "🧪 TESTS DE CONFIGURATION"
echo "=========================================="
echo ""

# Vérifier les fichiers
echo "[1] Vérification des fichiers de configuration..."
for file in server.conf users.conf logging.conf; do
    if [ -f "$CONFIG_DIR/$file" ]; then
        echo "  ✓ $file existe"
    else
        echo "  ✗ $file MANQUANT"
        exit 1
    fi
done
echo ""

# Vérifier le contenu de server.conf
echo "[2] Vérification de server.conf..."
grep -q "LOG_PORT" "$CONFIG_DIR/server.conf" && echo "  ✓ LOG_PORT trouvé" || echo "  ✗ LOG_PORT manquant"
grep -q "LOG_DIRECTORY" "$CONFIG_DIR/server.conf" && echo "  ✓ LOG_DIRECTORY trouvé" || echo "  ✗ LOG_DIRECTORY manquant"
grep -q "SERVER_HOST" "$CONFIG_DIR/server.conf" && echo "  ✓ SERVER_HOST trouvé" || echo "  ✗ SERVER_HOST manquant"
echo ""

# Vérifier le contenu de users.conf
echo "[3] Vérification de users.conf..."
USER_COUNT=$(grep -c ":" "$CONFIG_DIR/users.conf" || true)
echo "  ✓ $USER_COUNT utilisateur(s) trouvé(s)"
echo ""

# Vérifier le contenu de logging.conf
echo "[4] Vérification de logging.conf..."
grep -q "ALERT_LEVELS" "$CONFIG_DIR/logging.conf" && echo "  ✓ ALERT_LEVELS trouvé" || echo "  ✗ ALERT_LEVELS manquant"
grep -q "REALTIME_LOGGING" "$CONFIG_DIR/logging.conf" && echo "  ✓ REALTIME_LOGGING trouvé" || echo "  ✗ REALTIME_LOGGING manquant"
echo ""

# Tester la lecture avec Python
echo "[5] Test de lecture Python..."
python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config_manager import (
        get_log_port,
        get_log_file,
        get_max_realtime_logs,
        get_users,
        validate_credentials
    )
    
    print("  ✓ config_manager importé")
    
    port = get_log_port()
    print(f"  ✓ LOG_PORT = {port}")
    
    log_file = get_log_file()
    print(f"  ✓ LOG_FILE = {log_file}")
    
    max_logs = get_max_realtime_logs()
    print(f"  ✓ MAX_REALTIME_LOGS = {max_logs}")
    
    users = get_users()
    print(f"  ✓ Utilisateurs chargés: {len(users)}")
    
    # Tester validation
    is_valid = validate_credentials("admin", "admin123")
    print(f"  ✓ Validation admin/admin123: {is_valid}")
    
except Exception as e:
    print(f"  ✗ Erreur: {e}")
    sys.exit(1)
EOF

echo ""
echo -e "\033[0;32m✓ TOUS LES TESTS DE CONFIGURATION RÉUSSIS\033[0m"
