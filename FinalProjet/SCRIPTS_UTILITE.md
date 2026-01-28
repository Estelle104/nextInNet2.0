# 🔧 Scripts dans `backend/scripts/` - Utilité & Exécution

## ⚠️ Réponse directe

**NON**, les scripts `.sh` dans `backend/scripts/` **NE sont PAS nécessaires** pour le lancement du projet en production.

Ils sont uniquement des **outils de TEST & DÉVELOPPEMENT**.

---

## 📁 Liste des scripts disponibles

```
backend/scripts/
├── get_mac_address.py          ← Python (utilitaire)
├── socket_client.sh            ← Bash (test)
├── test_config.sh              ← Bash (test)
└── test_socket_communication.sh ← Bash (test)
```

---

## 🔍 Détail de chaque script

### 1️⃣ **`get_mac_address.py`** 🔌

#### Utilité
- Récupère les adresses MAC des interfaces réseau
- Identifie les appareils connectés

#### Exécution
```bash
# Manuelle (développement)
python3 backend/scripts/get_mac_address.py
```

#### Résultat
```
=== Adresses MAC des interfaces réseau ===

eth0: 00:1A:2B:3C:4D:5E
wlan0: 00:1A:2B:3C:4D:5F
wlo1: AA:BB:CC:DD:EE:FF
```

#### Utilisé dans le projet?
- ❌ **NON** - N'est jamais appelé automatiquement
- ✅ Utilisé manuellement pour configuration

**Conclusion:** `get_mac_address.py` = **OPTIONNEL** (utilitaire de diagnostic)

---

### 2️⃣ **`socket_client.sh`** 🔗

#### Utilité
- Teste les connexions **socket TCP** avec le serveur
- Envoie requêtes (`realtime`, `history`, etc.)
- Valide que le serveur répond

#### Exécution
```bash
# Appelé par test_socket_communication.sh UNIQUEMENT
bash backend/scripts/socket_client.sh 127.0.0.1 5050 realtime 5
```

#### Appelé par
```bash
# Ligne 65
test_socket_communication.sh:65  → socket_client.sh (realtime)

# Ligne 75
test_socket_communication.sh:75  → socket_client.sh (history)

# Ligne 86
test_socket_communication.sh:86  → socket_client.sh (invalid)
```

#### Utilisé en production?
- ❌ **NON** - Jamais appelé par le code Python
- ✅ Uniquement dans les **scripts de test**

**Conclusion:** `socket_client.sh` = **PUREMENT TEST** (non-essentiel)

---

### 3️⃣ **`test_config.sh`** ✅

#### Utilité
- Valide que les **fichiers de configuration** existent
- Vérifie les paramètres essentiels
- Teste l'importation Python des configurations

#### Exécution
```bash
# Manuelle (avant lancer le projet)
bash backend/scripts/test_config.sh
```

#### Valide
```
✓ server.conf existe
✓ users.conf existe  
✓ logging.conf existe
✓ LOG_PORT trouvé
✓ LOG_DIRECTORY trouvé
✓ ALERT_LEVELS trouvé
✓ 3 utilisateur(s) trouvé(s)
```

#### Appelé automatiquement?
- ❌ **NON** - Jamais appelé dans `start_system.sh`
- ✅ À lancer **manuellement** avant le démarrage

**Conclusion:** `test_config.sh` = **PRÉ-LANCEMENT** (diagnostic)

---

### 4️⃣ **`test_socket_communication.sh`** 🧪

#### Utilité
- Lance un **serveur socket de test**
- Teste les **3 types de requêtes** avec `socket_client.sh`
- Valide la communication TCP complète

#### Exécution
```bash
# Manuelle (tests complets)
bash backend/scripts/test_socket_communication.sh
```

#### Ce qu'il fait
```bash
1. Crée serveur socket sur port 9050
2. Appelle socket_client.sh (realtime)  → reçoit logs
3. Appelle socket_client.sh (history)   → reçoit historique
4. Appelle socket_client.sh (invalid)   → reçoit erreur
5. Valide les 3 résultats
6. Arrête le serveur
```

#### Appelé automatiquement?
- ❌ **NON** - Jamais appelé dans `start_system.sh`
- ✅ À lancer **manuellement** pour tests

**Conclusion:** `test_socket_communication.sh` = **SUITE DE TESTS** (validation)

---

## 📊 Tableau comparatif

| Script | Type | Automatique? | Utilité | Essentiel? |
|--------|------|-------------|---------|-----------|
| `get_mac_address.py` | Utilitaire | ❌ | Diagnostic interfaces | ❌ NON |
| `socket_client.sh` | Test | ❌ | Teste socket TCP | ❌ NON |
| `test_config.sh` | Test | ❌ | Valide configuration | ❌ NON |
| `test_socket_communication.sh` | Test | ❌ | Suite complète de tests | ❌ NON |

---

## 🚀 Flux réel du lancement du projet

```
bash start_system.sh
    │
    ├─ ✅ Vérification config système
    │
    ├─ ✅ Arrêt services conflictuels
    │
    ├─ ✅ Configuration IP du WiFi
    │
    ├─ ✅ Configuration NAT (iptables)
    │
    ├─ ✅ Lancement DHCP Server (Python)
    │   └─ python3 backend/serveur/dhcp_server.py
    │   └─ Port 67/UDP
    │
    ├─ ✅ Lancement TCP Server (Python)
    │   └─ python3 backend/serveur/tcp_server_simple.py
    │   └─ Port 5050/TCP
    │
    ├─ ✅ Lancement WiFi AP (hostapd)
    │   └─ hostapd /etc/hostapd/hostapd_*.conf
    │
    └─ ✅ Lancement GUI Frontend (Python)
        └─ python3 backend/client/client.py
        └─ Tkinter interface

        ↓
        
❌ LES SCRIPTS .SH NE SONT PAS APPELÉS
```

---

## 🧪 Flux des tests (optionnel)

```
bash test_config.sh                 ← TEST 1: Configuration
    │
    ├─ Vérifie fichiers .conf
    ├─ Vérifie paramètres
    └─ Valide imports Python

bash test_socket_communication.sh    ← TEST 2: Communication
    │
    ├─ Lance serveur socket
    ├─ Appelle socket_client.sh (3x)
    └─ Valide réponses

python3 get_mac_address.py          ← DIAGNOSTIC: Interfaces
    │
    └─ Affiche MACs des interfaces
```

---

## ✅ Quand utiliser les scripts?

### **Avant de lancer le projet** 🔍
```bash
# 1. Vérifier que la configuration est OK
bash backend/scripts/test_config.sh

# 2. Vérifier les interfaces réseau
python3 backend/scripts/get_mac_address.py

# 3. (Optionnel) Tester la communication socket
bash backend/scripts/test_socket_communication.sh
```

### **Pour lancer le projet en production** 🚀
```bash
# Juste lancer le démarrage
bash start_system.sh

# ❌ N'utiliser AUCUN script dans backend/scripts/
```

---

## 🎯 Cas d'usage complets

### **Cas 1: Diagnostic avant démarrage**
```bash
$ cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet

# Étape 1: Vérifier configuration
$ bash backend/scripts/test_config.sh 
  ✓ server.conf existe
  ✓ users.conf existe
  ✓ Tous les paramètres OK

# Étape 2: Vérifier interfaces réseau
$ python3 backend/scripts/get_mac_address.py
  eth0: 00:1A:2B:3C:4D:5E
  wlan0: AA:BB:CC:DD:EE:FF
  wlo1: 11:22:33:44:55:66

# Étape 3: Tests communication (optionnel)
$ bash backend/scripts/test_socket_communication.sh
  ✓ Serveur socket prêt
  ✓ Test realtime: OK
  ✓ Test history: OK
  ✓ Test invalid: OK

# Étape 4: Lancer le projet
$ bash start_system.sh
  ✓ SYSTÈME DÉMARRÉ
```

### **Cas 2: Lancer le projet directement**
```bash
$ cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet
$ bash start_system.sh
  ✓ SYSTÈME DÉMARRÉ
  
# ❌ Pas besoin d'utiliser les scripts dans backend/scripts/
```

### **Cas 3: Debug - Tester socket directement**
```bash
# Terminal 1: Lancer serveur socket
bash backend/scripts/socket_server.sh 9050 backend/logs/test.log start

# Terminal 2: Tester avec le client
bash backend/scripts/socket_client.sh 127.0.0.1 9050 realtime 5

# Résultat: Affiche les logs du serveur
```

---

## 📋 Résumé final

### **Scripts dans `backend/scripts/` :**

| Aspect | Réponse |
|--------|---------|
| **Nécessaires pour lancer?** | ❌ NON |
| **Appelés automatiquement?** | ❌ NON |
| **En production?** | ❌ NON |
| **Utilisés pour?** | ✅ Tests & Diagnostic |
| **Quand les utiliser?** | ✅ Avant lancer/debug |
| **Pour production utiliser?** | ✅ `bash start_system.sh` |

### **Hiérarchie des scripts de démarrage:**

```
Scripts de LANCEMENT (utiliser pour démarrer):
├─ bash start_system.sh           ← UTILISER POUR DÉMARRER ✅
├─ bash configure_ap.sh           ← Setup initial (une fois)
└─ bash start.sh                  ← Alternative simple

Scripts de TEST (utiliser pour valider):
├─ bash backend/scripts/test_config.sh ← Diagnostic config
├─ bash backend/scripts/test_socket_communication.sh ← Test sockets
└─ python3 backend/scripts/get_mac_address.py ← Diagnostic MAC
```

---

## 🎓 Conclusion

**Les scripts `.sh` dans `backend/scripts/` sont:**

✅ **UTILES pour:**
- Valider la configuration avant lancer
- Tester les connexions socket
- Diagnostiquer les problèmes

❌ **PAS NÉCESSAIRES pour:**
- Lancer le projet en production
- Fonctionnement normal du système
- Mode opérationnel

**Pour lancer le projet:** `bash start_system.sh`

**Pour tester avant:** Utiliser les scripts dans `backend/scripts/` (optionnel)
