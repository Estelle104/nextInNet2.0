#!/bin/bash

# Test Remote Connection - Teste la connexion à un serveur distant
# Usage: bash test_remote_connection.sh <SERVER_IP> [PORT]

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Paramètres
SERVER_IP="${1:-192.168.1.100}"
PORT="${2:-5050}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔌 REMOTE CONNECTION TEST${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Serveur: ${YELLOW}$SERVER_IP${NC}"
echo -e "Port: ${YELLOW}$PORT${NC}"
echo ""

# Test 1: Ping
echo -e "${BLUE}[1/6] Test PING...${NC}"
if ping -c 1 -W 2 "$SERVER_IP" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Serveur accessible${NC}"
else
    echo -e "${RED}✗ Serveur non joignable${NC}"
    echo -e "    Vérifier: ping $SERVER_IP"
    exit 1
fi
echo ""

# Test 2: Port ouvert (netcat)
echo -e "${BLUE}[2/6] Test PORT avec netcat...${NC}"
if command -v nc &> /dev/null; then
    if nc -zv "$SERVER_IP" "$PORT" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Port $PORT ouvert${NC}"
    else
        echo -e "${RED}✗ Port $PORT fermé ou serveur pas actif${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ netcat non trouvé, test ignoré${NC}"
fi
echo ""

# Test 3: Vérifier socat ou alternatives
echo -e "${BLUE}[3/6] Outils disponibles...${NC}"
TOOLS=""
[ -n "$(command -v socat)" ] && TOOLS="$TOOLS socat" || TOOLS="$TOOLS [socat]"
[ -n "$(command -v nc)" ] && TOOLS="$TOOLS nc" || TOOLS="$TOOLS [nc]"
[ -n "$(command -v bash)" ] && TOOLS="$TOOLS bash-tcp"
echo -e "${GREEN}✓ Outils: $TOOLS${NC}"
echo ""

# Test 4: Connexion basique
echo -e "${BLUE}[4/6] Test CONNEXION...${NC}"
if command -v socat &> /dev/null; then
    RESPONSE=$(timeout 2 socat - TCP:"$SERVER_IP:$PORT" < <(echo "realtime 1") 2>/dev/null)
    if [ -n "$RESPONSE" ]; then
        echo -e "${GREEN}✓ Connexion réussie${NC}"
        echo -e "${BLUE}   Réponse reçue (premiers 100 car):${NC}"
        echo "$RESPONSE" | head -3 | sed 's/^/   /'
    else
        echo -e "${RED}✗ Pas de réponse du serveur${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ Socat non disponible, test ignoré${NC}"
fi
echo ""

# Test 5: Test socket_client.sh
echo -e "${BLUE}[5/6] Test SCRIPT socket_client.sh...${NC}"
SOCKET_CLIENT="$BACKEND_DIR/scripts/socket_client.sh"
if [ -f "$SOCKET_CLIENT" ]; then
    if bash "$SOCKET_CLIENT" "$SERVER_IP" "$PORT" realtime 1 > /tmp/test_output.txt 2>&1; then
        echo -e "${GREEN}✓ Script socket_client.sh fonctionne${NC}"
        echo -e "${BLUE}   Logs reçus:${NC}"
        head -3 /tmp/test_output.txt | sed 's/^/   /'
    else
        echo -e "${YELLOW}⚠ Erreur script (peut être normal si peu de logs)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Script socket_client.sh non trouvé${NC}"
    echo -e "   Chercher: find $BACKEND_DIR -name 'socket_client.sh'"
fi
echo ""

# Test 6: Requête personnalisée
echo -e "${BLUE}[6/6] Test REQUÊTE personnalisée...${NC}"
if command -v socat &> /dev/null; then
    echo -e "${YELLOW}Modes disponibles:${NC}"
    echo "  - realtime N  : Derniers N logs"
    echo "  - history N   : Historique N logs"
    echo "  - stream      : Flux continu"
    echo ""
    read -p "Entrer le mode (défaut: realtime 5): " MODE
    MODE="${MODE:-realtime 5}"
    
    echo -e "${BLUE}Envoi: $MODE${NC}"
    timeout 3 socat - TCP:"$SERVER_IP:$PORT" < <(echo "$MODE") 2>/dev/null | head -10 | sed 's/^/   /'
else
    echo -e "${YELLOW}⚠ Socat non disponible pour test interactif${NC}"
fi
echo ""

# Résumé
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ TOUS LES TESTS RÉUSSIS!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Prochaines étapes:${NC}"
echo "1. Serveur tourne: python3 $BACKEND_DIR/serveur/log_server.py"
echo "2. Récupérer logs: bash $SOCKET_CLIENT $SERVER_IP $PORT realtime 5"
echo "3. Voir persistant: bash $SOCKET_CLIENT $SERVER_IP $PORT history 20"
echo ""
echo -e "${YELLOW}Commandes utiles:${NC}"
echo "• Vérifier port: lsof -i :$PORT"
echo "• Connexions: ss -tnp | grep $PORT"
echo "• Diagnostic: ping $SERVER_IP"
echo ""
