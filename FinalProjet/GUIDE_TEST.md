# Guide complet de test du projet FinalProjet

## 📋 Table des matières

1. [Tests rapides](#tests-rapides)
2. [Tests détaillés](#tests-détaillés)
3. [Test du serveur](#test-du-serveur)
4. [Test du frontend](#test-du-frontend)
5. [Test du flux complet](#test-du-flux-complet)
6. [Dépannage](#dépannage)

---

## Tests rapides

### 1️⃣ Vérifier les fichiers de configuration

```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend

# Vérifier que les fichiers existent
ls -la config/
# Résultat attendu:
# -rw-r--r-- server.conf
# -rw-r--r-- users.conf
# -rw-r--r-- logging.conf
```

### 2️⃣ Tester les configurations

```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/scripts

bash test_config.sh
```

Résultat attendu:
```
✓ LOG_PORT trouvé
✓ LOG_DIRECTORY trouvé
✓ SERVER_HOST trouvé
✓ Utilisateurs chargés: 4
✓ Validation admin/admin123: True
```

### 3️⃣ Tester la communication socket

```bash
bash test_socket_communication.sh
```

Résultat attendu:
```
✓ Serveur en écoute sur le port 9050
✓ Logs reçus
✓ Historique reçu (9 lignes)
✓ Erreur correctement rapportée
```

---

## Tests détaillés

### Test 1: Configuration centralisée

#### Vérifier que users_data.py charge depuis la config

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend')

from data.users_data import users
print(f"Utilisateurs chargés: {len(users)}")
for user in users:
    print(f"  - {user['username']}")
EOF
```

Résultat attendu:
```
Utilisateurs chargés: 4
  - admin
  - Miantsa
  - Estelle
  - Andry
```

#### Tester le module config_manager

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend')

from config_manager import (
    get_log_port,
    get_log_file,
    get_max_realtime_logs,
    validate_credentials
)

print(f"Port: {get_log_port()}")
print(f"Fichier de log: {get_log_file()}")
print(f"Max logs réels: {get_max_realtime_logs()}")
print(f"Test admin/admin123: {validate_credentials('admin', 'admin123')}")
print(f"Test admin/wrong: {validate_credentials('admin', 'wrong')}")
EOF
```

Résultat attendu:
```
Port: 5050
Fichier de log: ./logs/Connexion.log
Max logs réels: 10
Test admin/admin123: True
Test admin/wrong: False
```

---

## Test du serveur

### 1. Démarrer le serveur de logs

```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0

python3 FinalProjet/backend/serveur/log_server.py
```

Résultat attendu:
```
[INFO] Configuration du serveur de logs
  Port: 5050
  Fichier de logs: ./logs/Connexion.log
  Max logs temps réel: 10
[SUCCESS] Serveur de logs démarré
[INFO] Serveur en attente de connexions...
```

**Laisser le terminal ouvert** pour les tests suivants.

### 2. Tester en parallèle (dans un autre terminal)

#### Test 1: Récupérer les logs en temps réel

```bash
bash /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/scripts/socket_client.sh 127.0.0.1 5050 realtime 5
```

#### Test 2: Récupérer l'historique

```bash
bash /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/scripts/socket_client.sh 127.0.0.1 5050 history 5
```

#### Test 3: Ajouter un log et vérifier

```bash
# Ajouter une entrée de log
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend')
from serveur.log_server import log_entry

log_entry("192.168.1.50", "AA:BB:CC:DD:EE:50")
print("Log ajouté")
EOF

# Récupérer et vérifier
bash /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/scripts/socket_client.sh 127.0.0.1 5050 realtime 5
```

---

## Test du frontend

### 1. Tester l'authentification

```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0

python3 FinalProjet/backend/client/client.py
```

**Interface GUI apparaîtra**

#### Tester les credentials

| Utilisateur | Mot de passe | Résultat attendu |
|-------------|--------------|------------------|
| admin | admin123 | ✓ Connexion |
| Miantsa | 1234 | ✓ Connexion |
| admin | wrong | ✗ Erreur |
| unknown | pass | ✗ Erreur |

### 2. Tester la navigation

Une fois connecté, tester:

1. **Onglet "Gestion des Logs"**
   - Cliquer sur "Temps réel"
   - Cliquer sur "Historique"
   - Cliquer sur "🔄 Rafraîchir"
   - Vérifier que les logs s'affichent correctement

2. **Onglet "Gestion des Utilisateurs"**
   - Voir la liste des utilisateurs
   - Cliquer "Create New User"
   - Cliquer "Go to List User"
   - Vérifier la navigation

3. **Onglet "Notifications"**
   - Voir la liste des notifications
   - Cliquer sur une notification
   - Vérifier les détails et les couleurs

---

## Test du flux complet

### Scénario 1: Authentification et consultation des logs

```bash
# Terminal 1: Démarrer le serveur
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0
python3 FinalProjet/backend/serveur/log_server.py

# Terminal 2: Ajouter des logs de test
python3 << 'EOF'
import sys, time
sys.path.insert(0, '/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend')
from serveur.log_server import log_entry

for i in range(5):
    log_entry(f"192.168.1.{100+i}", f"AA:BB:CC:DD:EE:{100+i}")
    print(f"Log {i+1} ajouté")
    time.sleep(1)
EOF

# Terminal 3: Lancer le client
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0
python3 FinalProjet/backend/client/client.py

# Tester:
# 1. Login avec admin/admin123
# 2. Aller dans "Gestion des Logs"
# 3. Voir les 5 logs ajoutés
# 4. Cliquer "Historique" et voir tous les logs
```

### Scénario 2: Gestion des utilisateurs

```bash
# Dans l'application GUI:
# 1. Aller dans "Gestion des Utilisateurs"
# 2. Voir la liste des utilisateurs (admin, Miantsa, Estelle, Andry)
# 3. Cliquer "Create New User"
# 4. Entrer un nouveau nom d'utilisateur et mot de passe
# 5. Cliquer "Create User" (voir le message dans la console)
# 6. Cliquer "Go to List User" pour retourner à la liste
```

---

## Dépannage

### ❌ Erreur: "socket_client.sh non trouvé"

```bash
# Solution:
find /home/andry -name "socket_client.sh" -type f
chmod +x /path/to/socket_client.sh
```

### ❌ Erreur: "socat non trouvé"

```bash
# Installation:
sudo apt-get update
sudo apt-get install socat
```

### ❌ Port 5050 déjà utilisé

```bash
# Trouver le processus:
lsof -i :5050

# Changer le port dans backend/config/server.conf:
LOG_PORT=5051
```

### ❌ Erreur: "Aucun log disponible"

```bash
# Vérifier que le fichier de log existe:
ls -la FinalProjet/backend/logs/
cat FinalProjet/backend/logs/Connexion.log

# Ajouter des logs manuellement:
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend')
from serveur.log_server import log_entry
log_entry("192.168.1.100", "AA:BB:CC:DD:EE:FF")
EOF
```

### ❌ L'interface GUI se ferme immédiatement

```bash
# Vérifier les erreurs:
python3 FinalProjet/backend/client/client.py 2>&1 | head -50

# Vérifier que les imports marchent:
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend')
from config_manager import validate_credentials
print("Imports OK")
EOF
```

---

## ✅ Checklist de validation

- [ ] Les fichiers de configuration existent
- [ ] `test_config.sh` réussit
- [ ] `test_socket_communication.sh` réussit
- [ ] Le serveur démarre sans erreur
- [ ] Les logs peuvent être récupérés
- [ ] L'authentification fonctionne
- [ ] La navigation entre les vues fonctionne
- [ ] Les logs en temps réel s'affichent
- [ ] Les notifications s'affichent
- [ ] La gestion des utilisateurs fonctionne

**Tous les tests ✓ = Système opérationnel** 🎉
