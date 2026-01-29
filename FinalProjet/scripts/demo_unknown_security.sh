#!/bin/bash

# ============================================================================
# DÉMONSTRATION: Système de Sécurité - Utilisateurs Inconnus
# ============================================================================
# Ce script simule les différents scénarios et affiche les logs en temps réel
# ============================================================================

set -e

PROJECT_ROOT="/home/itu/S3/MrHaga/projet/nextInNet2.0/FinalProjet"
BACKEND_DIR="$PROJECT_ROOT/backend"
SERVER_SCRIPT="$BACKEND_DIR/serveur/tcp_server_simple.py"
NOTIFICATIONS_LOG="$PROJECT_ROOT/logs/notifications.log"
CONNEXION_LOG="$PROJECT_ROOT/logs/Connexion.log"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear_logs() {
    echo -n "" > "$NOTIFICATIONS_LOG" 2>/dev/null || true
    echo -n "" > "$CONNEXION_LOG" 2>/dev/null || true
    echo "[LOG] Logs nettoyés"
}

header() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}▶ $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

demo() {
    echo -e "${CYAN}» $1${NC}"
}

# Main Menu
show_menu() {
    clear
    header "DÉMONSTRATION: Gestion des Utilisateurs Inconnus"
    
    cat << 'EOF'
📋 SCÉNARIOS DISPONIBLES:

1️⃣  Machine AUTORISÉE (devices.conf)
    → Connexion acceptée, SSH autorisé

2️⃣  Machine INCONNUE - Idle 15s
    → Expulsion automatique après 15 secondes

3️⃣  Machine INCONNUE - Tentative SSH
    → BLOCAGE + PING + SHUTDOWN -h now

4️⃣  Machine BLOQUÉE (blocked_ips.conf)
    → Connexion refusée

5️⃣  Afficher tous les logs en temps réel

0️⃣  Quitter

EOF
    echo -n "Choisir un scénario [0-5]: "
    read -r choice
    return $choice
}

# Scénario 1: Machine autorisée
scenario_1() {
    header "SCÉNARIO 1: Machine AUTORISÉE"
    
    info "Vérification de devices.conf..."
    if grep -q "AA:BB:CC:DD:EE:FF" "$BACKEND_DIR/config/devices.conf" 2>/dev/null; then
        success "Machine autorisée trouvée dans devices.conf"
    else
        warning "Aucune machine autorisée dans devices.conf"
    fi
    
    demo "Simulation: Connexion depuis 192.168.43.100 (autorisée)"
    echo "echo 'test' | nc 192.168.43.100 5050"
    
    echo ""
    info "Comportement attendu:"
    echo "  ✓ Connexion acceptée"
    echo "  ✓ SSH autorisé"
    echo "  ✓ Notification: INFO"
    echo "  ✓ Pas d'expulsion"
    
    echo ""
    read -p "Appuyer sur Entrée pour afficher les logs..."
    tail -5 "$CONNEXION_LOG" 2>/dev/null | grep "autorisée" || echo "Aucun log"
}

# Scénario 2: Machine inconnue - timeout
scenario_2() {
    header "SCÉNARIO 2: Machine INCONNUE - Idle 15 Secondes"
    
    demo "Simulation: IP dynamique 192.168.43.155 se connecte"
    echo "echo 'test' | nc 192.168.43.155 5050"
    
    echo ""
    info "⏱️  Countdown: 15 secondes avant expulsion"
    
    echo ""
    info "Comportement attendu:"
    echo "  ⏱️  T=0s: Machine détectée (WARNING)"
    echo "  ⏱️  T=15s: Expulsion automatique"
    echo "  ❌ iptables DROP appliquée"
    echo "  📝 Ajoutée à blocked_ips.conf"
    
    echo ""
    read -p "Appuyer sur Entrée pour afficher les notifications..."
    tail -10 "$NOTIFICATIONS_LOG" 2>/dev/null | grep -E "WARNING|TIMEOUT|EXPULSION" || echo "Aucune notification"
}

# Scénario 3: Machine inconnue - SSH
scenario_3() {
    header "SCÉNARIO 3: Machine INCONNUE - Tentative SSH"
    
    demo "Simulation: IP dynamique 192.168.43.165 tente SSH"
    echo "ssh root@192.168.43.165"
    
    echo ""
    info "🔴 Actions automatiques:"
    echo "  1️⃣  Détection SSH (port 22)"
    echo "  2️⃣  BLOCAGE immédiat"
    echo "  3️⃣  PING de la machine"
    echo "  4️⃣  Envoi: ssh root@192.168.43.165 'shutdown -h now'"
    echo "  5️⃣  Machine éteinte (power off)"
    echo "  6️⃣  iptables DROP"
    echo "  7️⃣  Notification BLOCKED"
    
    echo ""
    info "Comportement attendu:"
    echo "  🚫 Connexion SSH bloquée"
    echo "  🔴 Ping de la cible"
    echo "  💤 Shutdown de la machine"
    echo "  📝 Ajoutée à blocked_ips.conf de manière permanente"
    
    echo ""
    read -p "Appuyer sur Entrée pour afficher les événements..."
    echo ""
    tail -15 "$NOTIFICATIONS_LOG" 2>/dev/null | grep -E "SSH|PING|SHUTDOWN" || echo "Aucun événement SSH"
}

# Scénario 4: Machine bloquée
scenario_4() {
    header "SCÉNARIO 4: Machine BLOQUÉE (blocked_ips.conf)"
    
    info "Vérification de blocked_ips.conf..."
    if [ -f "$BACKEND_DIR/config/blocked_ips.conf" ]; then
        echo ""
        echo "IPs bloquées actuelles:"
        echo "---"
        grep -v "^#" "$BACKEND_DIR/config/blocked_ips.conf" 2>/dev/null | grep -v "^$" || echo "Aucune IP bloquée"
        echo "---"
    fi
    
    demo "Simulation: Tentative de connexion d'une IP bloquée"
    echo "echo 'test' | nc 192.168.43.180 5050"
    
    echo ""
    info "Comportement attendu:"
    echo "  ❌ Connexion refusée immédiatement"
    echo "  🚫 Notification BLOCKED"
    echo "  iptables DROP appliquée"
    
    echo ""
    read -p "Appuyer sur Entrée pour afficher les logs..."
    tail -5 "$CONNEXION_LOG" 2>/dev/null | grep -i "bloquée" || echo "Aucun log de blocage"
}

# Scénario 5: Logs en temps réel
scenario_5() {
    header "LOGS EN TEMPS RÉEL"
    
    echo "Affichage des logs (Ctrl+C pour arrêter):"
    echo ""
    
    # Créer un processus en background qui affiche les logs
    tail -f "$NOTIFICATIONS_LOG" 2>/dev/null &
    TAIL_PID=$!
    
    trap "kill $TAIL_PID 2>/dev/null" EXIT
    
    # Garder le script alive
    wait $TAIL_PID 2>/dev/null || true
}

# Main loop
while true; do
    show_menu
    choice=$?
    
    case $choice in
        1) scenario_1 ;;
        2) scenario_2 ;;
        3) scenario_3 ;;
        4) scenario_4 ;;
        5) scenario_5 ;;
        0) echo "Au revoir! 👋"; exit 0 ;;
        *) error "Choix invalide" ;;
    esac
    
    echo ""
    read -p "Appuyer sur Entrée pour continuer..."
done
