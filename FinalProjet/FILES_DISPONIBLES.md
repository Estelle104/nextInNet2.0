# 📚 Fichiers de test disponibles

## 🎯 Quick Start

### Fichier: `TEST_INSTRUCTIONS.md`
**Location:** `/FinalProjet/TEST_INSTRUCTIONS.md`

Résume comment tester avec 3 options:
1. Test complet en une commande
2. Démarrage automatique
3. Tests manuels détaillés

### Fichier: `quick_test.sh`
**Location:** `/FinalProjet/quick_test.sh`

Test rapide (5-10 secondes) qui valide:
- Fichiers de configuration
- Imports Python
- Validation des credentials
- Chargement des utilisateurs

**Utilisation:**
```bash
bash quick_test.sh
```

### Fichier: `start.sh`
**Location:** `/FinalProjet/start.sh`

Lance l'application complète en 2 terminaux:
- Serveur de logs (terminal 1)
- Client GUI (terminal 2)

**Utilisation:**
```bash
bash start.sh
```

---

## 🔧 Tests détaillés

### Fichier: `run_all_tests.sh`
**Location:** `/FinalProjet/backend/scripts/run_all_tests.sh`

Suite complète de tests:
- Vérification des fichiers
- Tests de configuration
- Tests des scripts socket
- Tests des imports Python
- Tests de communication socket

**Utilisation:**
```bash
cd /FinalProjet/backend/scripts
bash run_all_tests.sh
```

### Fichier: `test_config.sh`
**Location:** `/FinalProjet/backend/scripts/test_config.sh`

Tests de configuration uniquement:
- Vérifie que les fichiers .conf existent
- Charge la configuration avec Python
- Valide les utilisateurs
- Teste la validation des credentials

**Utilisation:**
```bash
bash test_config.sh
```

**Résultat attendu:**
```
✓ server.conf chargé
✓ users.conf chargé (4 utilisateurs)
✓ Validation credentials OK
```

### Fichier: `test_socket_communication.sh`
**Location:** `/FinalProjet/backend/scripts/test_socket_communication.sh`

Tests de communication socket:
- Démarre un serveur socket de test
- Teste requêtes realtime
- Teste requêtes history
- Teste gestion des erreurs
- Arrête le serveur proprement

**Utilisation:**
```bash
bash test_socket_communication.sh
```

**Résultat attendu:**
```
✓ Serveur en écoute sur le port 9050
✓ Logs reçus
✓ Historique reçu (9 lignes)
✓ Erreur correctement rapportée
```

---

## 📖 Guides

### Fichier: `GUIDE_TEST.md`
**Location:** `/FinalProjet/GUIDE_TEST.md`

Guide complet de test incluant:
- Tests rapides
- Tests détaillés
- Test du serveur
- Test du frontend
- Test du flux complet
- Guide de dépannage
- Checklist de validation

### Fichier: `README_CONFIG.md`
**Location:** `/FinalProjet/backend/config/README_CONFIG.md`

Documentation de la configuration:
- Résumé des modifications
- Utilisation de la configuration
- Structure du projet
- Avantages de l'approche

### Fichier: `README_SOCKET.md`
**Location:** `/FinalProjet/backend/scripts/README_SOCKET.md`

Documentation des scripts socket:
- Architecture socket
- Utilisation des scripts
- Dépendances
- Testing

---

## 🚀 Flux de test recommandé

### Étape 1: Test rapide (1 minute)
```bash
cd /FinalProjet
bash quick_test.sh
```

### Étape 2: Démarrage complet (5 minutes)
```bash
bash start.sh
```
Puis tester dans l'interface GUI:
- Se connecter (admin/admin123)
- Cliquer sur les différents onglets
- Vérifier que tout fonctionne

### Étape 3: Tests détaillés (10 minutes)
```bash
cd backend/scripts
bash test_config.sh
bash test_socket_communication.sh
```

### Étape 4: Test de scenario complet (15 minutes)
Suivre le guide dans `GUIDE_TEST.md` > "Test du flux complet"

---

## ✅ Résumé des vérifications

| Test | Fichier | Commande |
|------|---------|----------|
| Rapide | quick_test.sh | `bash quick_test.sh` |
| Configuration | test_config.sh | `bash test_config.sh` |
| Socket | test_socket_communication.sh | `bash test_socket_communication.sh` |
| Tous les tests | run_all_tests.sh | `bash run_all_tests.sh` |
| Complet | start.sh | `bash start.sh` |

---

## 🎓 Compétences testées

✓ **Configuration** - Fichiers .conf chargés correctement  
✓ **Python** - Imports et modules fonctionnent  
✓ **Bash** - Scripts socket exécutables  
✓ **Communication** - Socket TCP fonctionne  
✓ **GUI** - Interface Tkinter fonctionne  
✓ **Authentification** - Credentials validés  
✓ **Logging** - Logs en temps réel  
✓ **Navigation** - Entre les vues  

---

## 📊 État du projet

- [x] Configuration externalisée
- [x] Scripts socket bash
- [x] Module config_manager
- [x] Serveur de logs Python
- [x] Client GUI Python
- [x] Gestion des utilisateurs
- [x] Logs en temps réel
- [x] Navigation entre vues
- [x] Suite complète de tests
- [x] Documentation de test

**Prêt pour la production!** 🎉
