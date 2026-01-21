#!/bin/bash

# Script de démarrage complet du projet FinalProjet
# Démarre le serveur et le client dans des terminaux séparés

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"

echo "🚀 Démarrage du projet FinalProjet"
echo "===================================="
echo ""

# Couleurs
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Rendre les scripts exécutables
chmod +x "$BACKEND_DIR/scripts"/*.sh

echo -e "${BLUE}[1] Test rapide...${NC}"
bash "$PROJECT_DIR/quick_test.sh" || {
    echo -e "${YELLOW}⚠ Certains tests ont échoué${NC}"
    read -p "Continuer quand même? (y/n) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
}

echo ""
echo -e "${BLUE}[2] Démarrage du serveur de logs...${NC}"
echo "Le serveur démarre sur le port 5050"
echo "Port configurable dans: $BACKEND_DIR/config/server.conf"
echo ""

# Vérifier si le terminal est disponible
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd '$PROJECT_DIR' && python3 $BACKEND_DIR/serveur/log_server.py; read -p 'Press Enter to close...'"
elif command -v xterm &> /dev/null; then
    xterm -hold -e "cd '$PROJECT_DIR' && python3 $BACKEND_DIR/serveur/log_server.py" &
elif command -v konsole &> /dev/null; then
    konsole -e "cd '$PROJECT_DIR' && python3 $BACKEND_DIR/serveur/log_server.py" &
else
    echo -e "${YELLOW}⚠ Aucun terminal graphique détecté${NC}"
    echo "Démarrage du serveur dans le terminal courant..."
    echo ""
    python3 "$BACKEND_DIR/serveur/log_server.py" &
    SERVER_PID=$!
fi

sleep 3

echo -e "${BLUE}[3] Démarrage du client...${NC}"
echo ""

cd "$PROJECT_DIR"
python3 "$BACKEND_DIR/client/client.py"

# Arrêter le serveur si lancé localement
if [ ! -z "$SERVER_PID" ]; then
    kill $SERVER_PID 2>/dev/null
fi

echo ""
echo -e "${GREEN}✓ Application fermée${NC}"
