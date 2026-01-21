#!/bin/bash

# Serveur TCP Simple - Enregistre les connexions et envoie les logs
# Port 5050

PORT=5050
LOG_FILE="/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/logs/Connexion.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Démarrage du serveur sur le port $PORT"

# Créer le fichier s'il n'existe pas
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

# Utiliser bash TCP redirect pour écouter
while true; do
    # Écouter les connexions
    exec 3<>/dev/tcp/0.0.0.0/$PORT || {
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ Erreur port $PORT déjà utilisé"
        exit 1
    }
    
    # Accepter les connexions (boucle infinie de clients)
    {
        read -t 5 request <&3
        
        # Récupérer l'IP du client (pas possible avec redirection, on utilise 0.0.0.0)
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$TIMESTAMP] [REQUEST] $request" >> "$LOG_FILE"
        
        # Envoyer les logs demandés
        if [[ "$request" =~ ^realtime ]]; then
            LIMIT=$(echo "$request" | awk '{print $2}')
            LIMIT="${LIMIT:-10}"
            tail -n "$LIMIT" "$LOG_FILE" >&3
        elif [[ "$request" =~ ^history ]]; then
            cat "$LOG_FILE" >&3
        else
            echo "[INFO] Commandes: realtime [N] | history" >&3
        fi
        
    } &
    
    wait
done
