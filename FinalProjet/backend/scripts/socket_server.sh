#!/bin/bash

# Script bash pour serveur socket TCP
# Gère la réception et l'envoi des logs via TCP avec support temps réel

HOST="0.0.0.0"
PORT="${1:-5050}"
LOG_FILE="${2:-Connexion.log}"

# Fonction pour démarrer le serveur socket avec streaming temps réel
start_socket_server() {
    echo "[INFO] Démarrage du serveur de logs sur le port $PORT" >&2
    echo "[INFO] Fichier de logs: $LOG_FILE" >&2
    
    # Créer le fichier de log s'il n'existe pas
    touch "$LOG_FILE"
    
    # Utiliser socat pour un serveur persistant avec support meilleur
    if command -v socat &> /dev/null; then
        echo "[INFO] Utilisation de socat pour le serveur socket" >&2
        # socat s'occupe du fork automatiquement
        socat -d -d TCP-LISTEN:$PORT,reuseaddr,fork SYSTEM:"handle_client" 2>&1
    else
        echo "[ERROR] socat non trouvé. Installation requise: apt-get install socat" >&2
        exit 1
    fi
}

# Fonction pour traiter chaque client
handle_client() {
    # Récupérer l'IP du client
    CLIENT_IP=$(echo "$SOCAT_PEERADDR" | cut -d: -f1)
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # ✅ ENREGISTRER la connexion
    if [ -n "$CLIENT_IP" ] && [ -n "$LOG_FILE" ]; then
        echo "[$TIMESTAMP] [CONNECTION] Client connected from $CLIENT_IP" >> "$LOG_FILE"
    fi
    
    # Lire la première ligne (type de log demandé)
    read -t 5 message
    
    if [ $? -ne 0 ]; then
        echo "[ERROR] Timeout ou erreur de lecture" >&2
        return 1
    fi
    
    message=$(echo "$message" | tr -d '\r\n')
    
    echo "[LOG] Reçu: $message de $CLIENT_IP" >&2
    
    case "$message" in
        realtime*)
            # Retourner les N derniers logs
            LIMIT=$(echo "$message" | awk '{print $2}')
            LIMIT="${LIMIT:-10}"
            if [ -f "$LOG_FILE" ]; then
                tail -n "$LIMIT" "$LOG_FILE"
            else
                echo "[INFO] Aucun log disponible"
            fi
            ;;
        history*)
            # Retourner tous les logs
            if [ -f "$LOG_FILE" ]; then
                cat "$LOG_FILE"
            else
                echo "[INFO] Aucun log disponible"
            fi
            ;;
        stream)
            # Mode streaming temps réel (suivi continu)
            if [ -f "$LOG_FILE" ]; then
                tail -n 1 "$LOG_FILE"
                tail -f "$LOG_FILE" 2>/dev/null &
                TAIL_PID=$!
                # Attendre la fermeture de la connexion
                sleep infinity
                kill $TAIL_PID 2>/dev/null
            else
                echo "[INFO] En attente de logs..."
            fi
            ;;
        *)
            echo "[ERROR] Type de log inconnu: $message"
            echo "[INFO] Commandes: realtime [N] | history | stream"
            ;;
    esac
}

# Export de la fonction pour socat
export -f handle_client

# Fonction pour enregistrer une connexion
log_connection() {
    local ip=$1
    local mac=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    {
        echo "$timestamp - Connexion de l'IP : $ip"
        echo "MAC Address: $mac"
        echo "---"
    } >> "$LOG_FILE"
}

# Interpréter les arguments
case "${3:-start}" in
    start)
        start_socket_server
        ;;
    log)
        log_connection "$4" "$5"
        ;;
    *)
        echo "Usage: $0 <port> <log_file> [start|log] [ip] [mac]"
        exit 1
        ;;
esac


