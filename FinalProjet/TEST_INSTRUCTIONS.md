# 🧪 COMMENT TESTER LE PROJET

## Option 1: Test complet en une commande ⚡

```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet
bash quick_test.sh
```

**Résultat attendu:** ✓ Tous les tests rapides réussis

---

## Option 2: Démarrage automatique 🚀

```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet
bash start.sh
```

Cela lancera:
1. ✓ Le test rapide
2. ✓ Le serveur de logs (dans un terminal)
3. ✓ Le client GUI (dans le terminal courant)

---

## Option 3: Tests manuels détaillés 🔍

### A. Test de configuration

```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/scripts
bash test_config.sh
```

**À vérifier:**
- ✓ Tous les fichiers .conf existent
- ✓ Les paramètres sont chargés correctement
- ✓ La validation des credentials fonctionne

### B. Test de communication socket

```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/scripts
bash test_socket_communication.sh
```

**À vérifier:**
- ✓ Le serveur démarre
- ✓ Les requêtes realtime/history fonctionnent
- ✓ Les erreurs sont correctement rapportées

### C. Test du serveur en isolé

**Terminal 1:**
```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0
python3 FinalProjet/backend/serveur/log_server.py
```

**Terminal 2:**
```bash
# Ajouter des logs
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend')
from serveur.log_server import log_entry

for i in range(3):
    log_entry(f"192.168.1.{100+i}", f"AA:BB:CC:DD:EE:{100+i}")
    print(f"Log {i+1} ajouté")
EOF

# Récupérer les logs
bash /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/scripts/socket_client.sh 127.0.0.1 5050 realtime 5
```

### D. Test du client GUI

**Terminal 1:** (Gardez le serveur en démarrage)
```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0
python3 FinalProjet/backend/serveur/log_server.py
```

**Terminal 2:**
```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0
python3 FinalProjet/backend/client/client.py
```

**Tests dans l'interface GUI:**

| Test | Étapes | Résultat attendu |
|------|--------|------------------|
| **Authentification** | Entrer: admin / admin123 | Accès à l'app |
| **Auth échouée** | Entrer: admin / wrong | Message d'erreur |
| **Logs réels** | Clic "Temps réel" | Les logs s'affichent |
| **Logs histoire** | Clic "Historique" | Tous les logs |
| **Rafraîchir** | Clic "🔄 Rafraîchir" | Mise à jour des logs |
| **Navigation users** | Clic "Gestion des Utilisateurs" | Liste des utilisateurs |
| **Create user** | Clic "Create New User" | Formulaire de création |
| **Retour liste** | Clic "Go to List User" | Retour à la liste |
| **Notifications** | Clic "Notifications" | Notifications affichées |
| **Détail notif** | Clic sur une notification | Détails visibles |

---

## 📋 Checklist avant publication

- [ ] Configuration externalisée dans `backend/config/`
- [ ] `quick_test.sh` réussit sans erreurs
- [ ] Serveur démarre correctement
- [ ] Client GUI se lance sans erreur
- [ ] L'authentification fonctionne (admin/admin123)
- [ ] Les logs s'affichent en temps réel
- [ ] La navigation entre les vues fonctionne
- [ ] Les notifications s'affichent correctement

---

## 🆘 Besoin d'aide?

### Erreur: "Port 5050 déjà utilisé"
```bash
# Solution 1: Modifier la configuration
nano FinalProjet/backend/config/server.conf
# Changer LOG_PORT=6000

# Solution 2: Tuer le processus
lsof -i :5050 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Erreur: "socat non trouvé"
```bash
# Installation
sudo apt-get update
sudo apt-get install socat
```

### Erreur: "Module non trouvé"
```bash
# Vérifier que vous êtes dans le bon répertoire
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0
```

### Les logs ne s'affichent pas
```bash
# Vérifier que le fichier de log existe
ls -la FinalProjet/backend/logs/

# Ajouter manuellement un log
python3 FinalProjet/backend/serveur/log_server.py &
sleep 2

python3 << 'EOF'
import sys
sys.path.insert(0, 'FinalProjet/backend')
from serveur.log_server import log_entry
log_entry("192.168.1.100", "AA:BB:CC:DD:EE:FF")
print("Log ajouté")
EOF
```

---

## 📊 Architecture testée

```
FinalProjet/
├── ✓ Configuration externalisée
├── ✓ Serveur socket bash
├── ✓ Client socket bash
├── ✓ Serveur de logs Python
├── ✓ Client GUI Python
└── ✓ Gestion des utilisateurs
```

---

**Vous êtes prêt? Lancez:** `bash quick_test.sh` 🎉
