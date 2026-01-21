#!/bin/bash

# Script pour tester la communication socket sans Python
# Teste les scripts bash socket_client et socket_server

LOG_FILE="test_socket.log"
PORT=5050

echo "========================================="
echo "Test de communication socket en bash"
echo "========================================="

# Créer un fichier de log de test
mkdir -p logs
TEST_LOG="logs/test.log"
echo "Test log entry 1" > "$TEST_LOG"
echo "Test log entry 2" >> "$TEST_LOG"
echo "Test log entry 3" >> "$TEST_LOG"

# Démarrer le serveur socket en arrière-plan
echo "[1] Démarrage du serveur socket..."
bash socket_server.sh $PORT "$TEST_LOG" start &
SERVER_PID=$!

# Attendre que le serveur démarre
sleep 2

# Tester la requête realtime
echo "[2] Test: Récupération des logs en temps réel..."
bash socket_client.sh 127.0.0.1 $PORT realtime 5
if [ $? -eq 0 ]; then
    echo "✓ Test realtime réussi"
else
    echo "✗ Test realtime échoué"
fi

# Tester la requête history
echo "[3] Test: Récupération de l'historique..."
bash socket_client.sh 127.0.0.1 $PORT history 5
if [ $? -eq 0 ]; then
    echo "✓ Test history réussi"
else
    echo "✗ Test history échoué"
fi

# Arrêter le serveur
echo "[4] Arrêt du serveur..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo "========================================="
echo "Tests terminés"
echo "========================================="
