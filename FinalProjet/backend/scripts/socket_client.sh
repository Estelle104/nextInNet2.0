#!/bin/bash

# Script bash pour client socket TCP
# Envoie des requêtes et reçoit les logs via TCP sans utiliser les sockets Python

HOST="${1:-127.0.0.1}"
PORT="${2:-5050}"
LOG_TYPE="${3:-realtime}"
TIMEOUT="${4:-5}"

# Fonction pour récupérer les logs via socket TCP
fetch_logs() {
    local host=$1
    local port=$2
    local log_type=$3
    local timeout=$4
    
    # Essayer avec socat d'abord (plus fiable)
    if command -v socat &> /dev/null; then
        echo "$log_type" | socat - TCP:$host:$port,connect-timeout=$timeout 2>/dev/null
        return $?
    fi
    
    # Sinon, utiliser exec avec redirection bash
    if (echo "$log_type"; sleep 0.1) | timeout $timeout bash -c "cat > /dev/tcp/$host/$port; cat < /dev/tcp/$host/$port" 2>/dev/null; then
        return 0
    fi
    
    # Dernier recours: utiliser nc (netcat)
    if command -v nc &> /dev/null; then
        echo "$log_type" | nc -w $timeout $host $port 2>/dev/null
        return $?
    fi
    
    echo "[ERROR] Aucun outil socket disponible (socat, bash TCP, ou nc)"
    return 1
}

# Exécuter la fonction
fetch_logs "$HOST" "$PORT" "$LOG_TYPE" "$TIMEOUT"
exit $?

