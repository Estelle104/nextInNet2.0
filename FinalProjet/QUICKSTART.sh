#!/bin/bash

# ============================================================================
# 🚀 QUICKSTART: Système de Sécurité - Utilisateurs Inconnus
# ============================================================================
# Ce guide accélère la mise en place du système
# ============================================================================

PROJECT_ROOT="/home/itu/S3/MrHaga/projet/nextInNet2.0/FinalProjet"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 QUICKSTART: Déployer le Système de Sécurité"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

success() { echo -e "${GREEN}✅ $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
step() { echo -e "${CYAN}▶ $1${NC}"; }

# Step 1: Vérifier les prérequis
step "ÉTAPE 1: Vérification des prérequis"
echo ""

# Python3
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    success "Python3 trouvé ($PYTHON_VERSION)"
else
    error "Python3 non trouvé. Installer: sudo apt install python3"
    exit 1
fi

# nc (netcat)
if command -v nc &> /dev/null; then
    success "netcat trouvé"
else
    warning "netcat non trouvé. Installer: sudo apt install netcat-openbsd"
fi

# ssh
if command -v ssh &> /dev/null; then
    success "ssh trouvé"
else
    warning "ssh non trouvé. Installer: sudo apt install openssh-client"
fi

# ping
if command -v ping &> /dev/null; then
    success "ping trouvé"
else
    warning "ping non trouvé"
fi

echo ""
step "ÉTAPE 2: Vérification des fichiers"
echo ""

# Vérifier les fichiers clés
FILES=(
    "$PROJECT_ROOT/backend/serveur/tcp_server_simple.py"
    "$PROJECT_ROOT/backend/config/devices.conf"
    "$PROJECT_ROOT/backend/config/blocked_ips.conf"
    "$PROJECT_ROOT/scripts/test_unknown_user_security.sh"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        success "Trouvé: $(basename $file)"
    else
        error "Manquant: $file"
    fi
done

echo ""
step "ÉTAPE 3: Syntaxe du serveur Python"
echo ""

if python3 -m py_compile "$PROJECT_ROOT/backend/serveur/tcp_server_simple.py" 2>/dev/null; then
    success "Syntaxe correcte"
else
    error "Erreur de syntaxe dans tcp_server_simple.py"
    exit 1
fi

echo ""
step "ÉTAPE 4: Préparation des logs"
echo ""

mkdir -p "$PROJECT_ROOT/logs"
touch "$PROJECT_ROOT/logs/Connexion.log"
touch "$PROJECT_ROOT/logs/notifications.log"

success "Dossier logs préparé"
success "Fichiers log créés"

echo ""
step "ÉTAPE 5: Configuration initiale"
echo ""

# Afficher la configuration
echo "Configuration actuelle:"
echo ""
echo "  ⏱️  Timeout inactivité: 15 secondes"
echo "  🔴 Plage IP inconnue: 150-200"
echo "  🔐 Plage IP autorisée: 100-149"
echo "  🔒 Détection SSH: Port 22 + mots-clés"
echo "  🛡️  Action SSH inconnue: PING + SHUTDOWN"
echo ""

echo "ℹ️  Modifier dans $PROJECT_ROOT/backend/serveur/tcp_server_simple.py:"
echo "  - TIMEOUT_UNKNOWN = 15 (ligne ~20)"
echo ""

echo ""
step "ÉTAPE 6: Vérification de sudo (recommandé)"
echo ""

if sudo -l | grep -q "iptables" 2>/dev/null; then
    success "iptables autorisé en sudo"
else
    warning "iptables peut nécessiter un mot de passe en sudo"
    echo "   Ajouter à sudoers pour éviter les prompts:"
    echo "   sudo visudo"
    echo "   Ajouter: $USER ALL=(ALL) NOPASSWD: /sbin/iptables"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 PRÊT À DÉMARRER!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📚 DOCUMENTATION:"
echo "  1. UNKNOWN_USER_SECURITY.md     - Détails complets"
echo "  2. INTEGRATION_GUIDE.md         - Guide d'intégration"
echo "  3. SECURITY_POLICY.md           - Politique de sécurité"
echo ""

echo "🚀 DÉMARRER LE SERVEUR:"
echo ""
echo "   cd $PROJECT_ROOT"
echo "   python3 backend/serveur/tcp_server_simple.py"
echo ""

echo "🧪 TESTER LE SYSTÈME:"
echo ""
echo "   # Terminal 1: Lancer le serveur"
echo "   python3 backend/serveur/tcp_server_simple.py"
echo ""
echo "   # Terminal 2: Afficher les logs"
echo "   tail -f logs/notifications.log"
echo ""
echo "   # Terminal 3: Simuler une connexion inconnue"
echo "   echo 'test' | nc 192.168.43.155 5050"
echo ""
echo "   # Attendre 15 secondes..."
echo "   # Vérifier l'expulsion: tail logs/notifications.log"
echo ""

echo "🎬 MODE DÉMO (INTERACTIF):"
echo ""
echo "   bash scripts/demo_unknown_security.sh"
echo ""

echo "✅ TEST COMPLET:"
echo ""
echo "   bash scripts/test_unknown_user_security.sh"
echo ""

echo ""
read -p "Appuyer sur Entrée pour quitter..."
echo ""
success "Configuration complète! Vous pouvez maintenant démarrer le serveur."
