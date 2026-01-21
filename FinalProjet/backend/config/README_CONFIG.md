# Configuration Externalisée et Gestion des Logs en Temps Réel

## Résumé des modifications

### 1. **Externalisation des données**

Toutes les données en dur du code ont été externalisées dans des fichiers de configuration:

#### Fichiers de configuration créés:
- **`backend/config/server.conf`** - Configuration du serveur (ports, répertoires, timeouts)
- **`backend/config/users.conf`** - Utilisateurs et mots de passe
- **`backend/config/logging.conf`** - Paramètres de logging et alertes

#### Module de gestion des configurations:
- **`backend/config_manager.py`** - Module centralisé pour charger et accéder aux configurations

### 2. **Fichiers modifiés**

#### `backend/data/users_data.py`
- Avant: Données utilisateur en dur dans le code
- Après: Charge les utilisateurs depuis `config/users.conf`

#### `backend/serveur/log_server.py`
- Avant: Port et répertoire hardcodés
- Après: Charge depuis `server.conf` et `logging.conf`
- Amélioration: Support du nombre de logs configurable

#### `backend/client/client.py`
- Avant: Utilisait un fichier `credentials.txt` en dur
- Après: Utilise le système de configuration centralisé avec `validate_credentials()`

#### `frontend/views/logs_view.py`
- Avant: Chargement synchrone des logs
- Après: 
  - Chargement asynchrone en arrière-plan (threading)
  - Bouton de rafraîchissement manuel
  - Barre de statut pour le retour
  - Support des messages [INFO]

### 3. **Amélioration de la gestion des logs en temps réel**

#### Serveur socket (`backend/scripts/socket_server.sh`):
- Nouvelle commande `stream` pour le suivi temps réel continu
- Meilleure gestion des connexions avec socat
- Fichier de log créé automatiquement

#### Client socket (`frontend/views/logs_view.py`):
- Chargement asynchrone pour ne pas bloquer l'interface
- Rafraîchissement manuel avec bouton
- Barre de statut informative
- Meilleure gestion des erreurs

## Utilisation

### Modifier la configuration

**Ajouter un nouvel utilisateur:**
```bash
# Éditer backend/config/users.conf
echo "nouveau_user:mot_de_passe" >> backend/config/users.conf
```

**Changer le port du serveur:**
```bash
# Éditer backend/config/server.conf
LOG_PORT=6000
```

**Modifier les paramètres de logging:**
```bash
# Éditer backend/config/logging.conf
MAX_REALTIME_LOGS=20
```

### Accéder aux configurations en Python

```python
from config_manager import (
    get_log_port,
    get_log_file,
    get_max_realtime_logs,
    get_users,
    validate_credentials
)

# Utilisation
port = get_log_port()
users = get_users()
is_valid = validate_credentials("admin", "admin123")
```

## Architecture

```
FinalProjet/
├── backend/
│   ├── config/
│   │   ├── server.conf        # Configuration serveur
│   │   ├── users.conf         # Utilisateurs
│   │   └── logging.conf       # Logging et alertes
│   ├── config_manager.py      # Gestionnaire de config
│   ├── data/
│   │   └── users_data.py      # Charge depuis config
│   ├── serveur/
│   │   └── log_server.py      # Serveur logs
│   ├── scripts/
│   │   ├── socket_server.sh   # Serveur socket
│   │   └── socket_client.sh   # Client socket
│   └── client/
│       └── client.py          # Client Python
└── frontend/
    └── views/
        └── logs_view.py       # Affichage des logs
```

## Avantages

✅ **Séparation des données et du code** - Facilite la maintenance  
✅ **Configurations externalisées** - Pas besoin de recompiler  
✅ **Chargement asynchrone** - Interface responsive  
✅ **Gestion temps réel améliorée** - Logs en temps réel sans bloquer  
✅ **Centralisation** - Un seul point d'accès pour les configs  
