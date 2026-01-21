# Communication Socket sans Python

Ce document explique comment le projet utilise des scripts bash pour gérer la communication socket au lieu d'utiliser directement le module `socket` de Python.

## Architecture

### Scripts bash disponibles

1. **socket_server.sh** - Serveur TCP pour recevoir et envoyer les logs
   - Démarre un serveur TCP sur le port spécifié
   - Utilise `socat` ou `nc` (netcat) pour les connexions
   - Gère les requêtes "realtime" et "history"

2. **socket_client.sh** - Client TCP pour communiquer avec le serveur
   - Envoie des requêtes au serveur socket
   - Récupère les logs via la connexion TCP
   - Utilise `socat`, redirection bash, ou `nc`

3. **test_socket.sh** - Script de test pour valider la communication

## Utilisation

### Démarrer le serveur

```bash
bash socket_server.sh 5050 ./logs/Connexion.log start
```

### Récupérer les logs (realtime)

```bash
bash socket_client.sh 127.0.0.1 5050 realtime 5
```

### Récupérer les logs (history)

```bash
bash socket_client.sh 127.0.0.1 5050 history 5
```

## Modifications dans le code Python

### log_server.py

Le fichier `log_server.py` ne crée plus de socket Python directement. À la place:

- Il lance le script `socket_server.sh` en arrière-plan via `subprocess`
- Fournit les fonctions `log_entry()` et `get_logs()` pour gérer les logs
- Toute la communication socket est gérée par le script bash

### logs_view.py

Le fichier `logs_view.py` utilise maintenant `subprocess` pour appeler le client socket:

- Appelle `socket_client.sh` via `subprocess.run()`
- Transmet les paramètres (host, port, log_type, timeout)
- Récupère la sortie du script bash

## Avantages de cette approche

1. **Pas de dépendances Python socket** - Tout est en bash natif
2. **Flexibilité** - Peut fonctionner avec différents outils (socat, nc, redirection bash)
3. **Transparence** - Les scripts peuvent être testés indépendamment
4. **Portabilité** - Fonctionne sur n'importe quel système Unix/Linux

## Dépendances requises

- `bash` (version 3.0+)
- Au moins l'un des éléments suivants:
  - `socat` (recommandé)
  - `netcat` / `nc`
  - Bash 3.0+ (pour la redirection `/dev/tcp`)

## Testing

Pour tester la communication socket:

```bash
bash test_socket.sh
```

Cela démarre un serveur de test, effectue des requêtes, puis arrête le serveur.
