#!/bin/bash

# 🚀 RÉFÉRENCE RAPIDE - Commandes essentielles

# ============================================
# SECTION 1: TEST RAPIDE
# ============================================

# Test complet en 10 secondes
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet && bash quick_test.sh

# ============================================
# SECTION 2: DÉMARRAGE COMPLET
# ============================================

# Démarrer serveur + client
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet && bash start.sh

# OU manuellement:

# Terminal 1: Démarrer le serveur
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0
python3 FinalProjet/backend/serveur/log_server.py

# Terminal 2: Démarrer le client
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0
python3 FinalProjet/backend/client/client.py

# ============================================
# SECTION 3: TESTS INDIVIDUELS
# ============================================

# Test 1: Configuration
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/scripts
bash test_config.sh

# Test 2: Socket
bash test_socket_communication.sh

# Test 3: Tous les tests
bash run_all_tests.sh

# ============================================
# SECTION 4: AJOUTER DES LOGS DE TEST
# ============================================

python3 << 'EOF'
import sys
sys.path.insert(0, '/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend')
from serveur.log_server import log_entry

# Ajouter 5 logs
for i in range(5):
    log_entry(f"192.168.1.{100+i}", f"AA:BB:CC:DD:EE:{100+i}")
    print(f"✓ Log {i+1} ajouté")
EOF

# ============================================
# SECTION 5: CONFIGURATION
# ============================================

# Afficher la configuration
cat /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/config/server.conf

# Modifier le port (exemple: 6000)
sed -i 's/LOG_PORT=5050/LOG_PORT=6000/' /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/config/server.conf

# Ajouter un utilisateur
echo "nouveau_user:mot_de_passe" >> /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/config/users.conf

# ============================================
# SECTION 6: DÉPANNAGE
# ============================================

# Vérifier que socat est installé
which socat || sudo apt-get install socat

# Vérifier le port
lsof -i :5050 || echo "Port libre"

# Tuer un processus
pkill -f "log_server.py" || echo "Pas de serveur actif"

# Voir les logs
cat /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/logs/Connexion.log

# Effacer les logs
rm /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/logs/Connexion.log

# ============================================
# SECTION 7: PYTHON DIRECTS
# ============================================

# Tester config_manager
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend')
from config_manager import validate_credentials, get_users
print(f"Utilisateurs: {get_users()}")
print(f"Test admin/admin123: {validate_credentials('admin', 'admin123')}")
EOF

# Tester users_data
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend')
from data.users_data import users
for u in users:
    print(f"- {u['username']}")
EOF

# Récupérer les logs en temps réel
bash /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/scripts/socket_client.sh 127.0.0.1 5050 realtime 5

# ============================================
# SECTION 8: DOCUMENTATION
# ============================================

# Lire le guide de test
cat /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/GUIDE_TEST.md

# Lire les instructions de test
cat /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/TEST_INSTRUCTIONS.md

# Lire la configuration
cat /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/config/README_CONFIG.md

# ============================================
# SECTION 9: RACCOURCIS UTILES
# ============================================

# Aller au répertoire du projet
alias go_project='cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0'

# Démarrer le serveur
alias start_server='cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0 && python3 FinalProjet/backend/serveur/log_server.py'

# Démarrer le client
alias start_client='cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0 && python3 FinalProjet/backend/client/client.py'

# Test rapide
alias quick_test='cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet && bash quick_test.sh'

# ============================================
# NOTES
# ============================================

# 1. Tous les chemins sont absolus - vous pouvez les copier-coller
# 2. Les commandes Python supposent que vous partez du bon répertoire
# 3. Le serveur doit être lancé AVANT le client
# 4. Les logs réels se trouvent dans: FinalProjet/backend/logs/
# 5. La configuration est dans: FinalProjet/backend/config/
# 6. Les scripts bash sont dans: FinalProjet/backend/scripts/

echo "✓ Prêt? Lancez: quick_test"
