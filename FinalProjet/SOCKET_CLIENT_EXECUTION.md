# 📍 Où est exécuté `socket_client.sh` ?

## 🔍 Résumé rapide

Le script `socket_client.sh` **n'est PAS exécuté automatiquement** dans le flux principal du code. C'est un **script utilitaire de TEST** qui a deux usages :

1. ✅ **Scripts de test** - Exécuté par `test_socket_communication.sh`
2. 📋 **Documentation** - Fourni dans les instructions de test
3. ❌ **PAS** exécuté par le code Python en production

---

## 🗺️ Localisation dans l'arborescence

```
backend/scripts/
├── socket_client.sh          ← FICHIER EN QUESTION
├── socket_server.sh          ← Script serveur (test)
├── test_socket_communication.sh  ← L'APPELLE (ligne 65, 75, 86)
├── test_config.sh
└── ...autres scripts...
```

---

## 🎯 Où et comment il est exécuté ?

### **1️⃣ Dans les scripts de TEST** 🧪

#### Lieu: `test_socket_communication.sh` (Lines 65-86)

```bash
# Script: backend/scripts/test_socket_communication.sh

# Ligne 65 - Test 1: Requête realtime
RESULT=$(bash "$SCRIPT_DIR/socket_client.sh" 127.0.0.1 $PORT realtime 5)

# Ligne 75 - Test 2: Requête history  
RESULT=$(bash "$SCRIPT_DIR/socket_client.sh" 127.0.0.1 $PORT history 5)

# Ligne 86 - Test 3: Requête invalide
RESULT=$(bash "$SCRIPT_DIR/socket_client.sh" 127.0.0.1 $PORT invalid 5)
```

**Déclenchement:**
```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/scripts
bash test_socket_communication.sh
```

**Flux d'exécution:**
```
┌─────────────────────────────────────────────────┐
│ test_socket_communication.sh (LANCEUR)          │
├─────────────────────────────────────────────────┤
│                                                  │
│ 1. Crée serveur socket (socket_server.sh)       │
│    ├─ Écoute port 9050                          │
│    └─ Prêt à recevoir requêtes                  │
│                                                  │
│ 2. Lance 3 tests:                               │
│    ├─ Test 1: bash socket_client.sh ... realtime
│    ├─ Test 2: bash socket_client.sh ... history
│    └─ Test 3: bash socket_client.sh ... invalid
│                                                  │
│ 3. Valide les réponses                          │
│    ├─ Vérifie si données reçues ✓              │
│    └─ Vérifie si erreurs correctes ✓            │
│                                                  │
│ 4. Arrête le serveur socket                    │
│                                                  │
└─────────────────────────────────────────────────┘
            ⬇️ socket_client.sh appelé 3x
┌─────────────────────────────────────────────────┐
│ socket_client.sh (CLIENT SOCKET)                │
├─────────────────────────────────────────────────┤
│                                                  │
│ Fonction: fetch_logs($host, $port, $type, ...)  │
│                                                  │
│ Essaie (dans cet ordre):                        │
│ 1. socat (PRÉFÉRÉ)                              │
│ 2. bash /dev/tcp (alternative)                  │
│ 3. netcat/nc (fallback)                         │
│                                                  │
│ Envoie requête: realtime / history / invalid    │
│ Reçoit réponse du serveur                       │
│ Affiche résultat                                │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

### **2️⃣ Dans la Documentation de TEST** 📄

#### Fichier: `TEST_INSTRUCTIONS.md` (Line 76)

```bash
# Exemple manuel d'utilisation
bash /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/scripts/socket_client.sh 127.0.0.1 5050 realtime 5
```

Cet exemple montre comment l'utiliser manuellement pour tests directs.

---

### **3️⃣ PAS utilisé en production** ❌

Le **code Python en production** n'appelle PAS ce script :

```python
# ❌ N'EXISTE PAS dans le code production:
subprocess.run(["bash", "socket_client.sh", ...])

# À la place, le code Python utilise:
# ✅ Import directs des modules
# ✅ Lectures de fichiers de logs
# ✅ Connexions socket natives Python
```

**Preuve:**
- `logs_view.py` (GUI) lit directement les fichiers de logs
- `tcp_server_simple.py` (Serveur) utilise sockets Python natifs
- Aucun appel subprocess à `socket_client.sh` en production

---

## 📊 Schéma: Quand socket_client.sh s'exécute

```
DÉMARRAGE SYSTÈME
    │
    ├─ bash start_system.sh           ← Production
    │   ├─ DHCP Server (Python)       ✓
    │   ├─ TCP Server (Python)        ✓
    │   └─ GUI Frontend (Tkinter)     ✓
    │
    └─ bash test_socket_communication.sh  ← TEST UNIQUEMENT
        ├─ Démarre serveur test socket
        ├─ bash socket_client.sh (3 fois)  ← EXÉCUTION
        └─ Valide résultats
```

---

## 🔧 Signature & Utilisation

### Signature
```bash
./socket_client.sh <host> <port> <log_type> <timeout>
```

### Paramètres
- **host**: Adresse serveur (ex: 127.0.0.1)
- **port**: Port du serveur (ex: 5050)
- **log_type**: Type de requête (realtime, history, autre)
- **timeout**: Délai max en secondes (ex: 5)

### Exemples d'exécution

```bash
# Test temps réel
./socket_client.sh 127.0.0.1 5050 realtime 5

# Test historique
./socket_client.sh 127.0.0.1 5050 history 5

# Serveur distant
./socket_client.sh 192.168.1.100 5050 realtime 10

# Avec timeout court
./socket_client.sh localhost 5050 realtime 2
```

---

## 📍 Code qui l'appelle

### Fichier: `test_socket_communication.sh`

```bash
#!/bin/bash

# Ligne 65-67: TEST 1
RESULT=$(bash "$SCRIPT_DIR/socket_client.sh" 127.0.0.1 $PORT realtime 5)
if echo "$RESULT" | grep -q "2026"; then
    echo "  ✓ Logs reçus (sample): $(echo "$RESULT" | head -1)"

# Ligne 75-78: TEST 2
RESULT=$(bash "$SCRIPT_DIR/socket_client.sh" 127.0.0.1 $PORT history 5)
LINE_COUNT=$(echo "$RESULT" | wc -l)
if [ $LINE_COUNT -gt 0 ]; then
    echo "  ✓ Historique reçu ($LINE_COUNT lignes)"

# Ligne 86-89: TEST 3
RESULT=$(bash "$SCRIPT_DIR/socket_client.sh" 127.0.0.1 $PORT invalid 5)
if echo "$RESULT" | grep -q "ERROR"; then
    echo "  ✓ Erreur correctement rapportée"
```

---

## ⚙️ Ce que le script fait

```
socket_client.sh
    │
    ├─ Lit paramètres ($HOST, $PORT, $LOG_TYPE, $TIMEOUT)
    │
    ├─ Essaie socat (si disponible)
    │   └─ echo "$LOG_TYPE" | socat - TCP:$host:$port
    │
    ├─ Sinon essaie bash /dev/tcp
    │   └─ (echo "$LOG_TYPE"; sleep 0.1) | bash -c "cat > /dev/tcp/..."
    │
    ├─ Sinon essaie nc (netcat)
    │   └─ echo "$LOG_TYPE" | nc -w $TIMEOUT $host $port
    │
    └─ Retourne la réponse du serveur

RÉSULTAT:
    ├─ Affiche les logs reçus du serveur
    └─ Retourne code sortie (0=succès, 1=erreur)
```

---

## 🎬 Cas d'usage complet

### Cas 1: Lancer les tests
```bash
$ cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/scripts
$ bash test_socket_communication.sh

=========================================
🧪 TESTS DE COMMUNICATION SOCKET
=========================================

✓ socat détecté

[1] Démarrage du serveur socket sur le port 9050...
  Serveur PID: 12345

[2] Vérification que le serveur est en écoute...
  ✓ Serveur en écoute sur le port 9050

[3] Test: Requête realtime...
  ✓ Logs reçus (sample): 2026-01-20 10:15:32 - Connexion de l'IP : 192.168.1.100

[4] Test: Requête history...
  ✓ Historique reçu (3 lignes)

[5] Test: Requête invalide...
  ✓ Erreur correctement rapportée

[6] Arrêt du serveur...
  ✓ Serveur arrêté
```

### Cas 2: Test manuel direct
```bash
$ bash socket_client.sh 127.0.0.1 5050 realtime 5

2026-01-20 10:15:32 - Connexion de l'IP : 192.168.1.100
MAC Address: AA:BB:CC:DD:EE:FF
---
2026-01-20 10:15:35 - Connexion de l'IP : 192.168.1.101
...
```

---

## 📋 Tableau récapitulatif

| Aspect | Détail |
|--------|---------|
| **Fichier** | `backend/scripts/socket_client.sh` |
| **Type** | Script utilitaire de test |
| **Exécuté par** | `test_socket_communication.sh` (3 appels) |
| **Mode de production** | ❌ NON exécuté |
| **Utilisé pour** | Tester communication socket TCP |
| **Paramètres** | host, port, log_type, timeout |
| **Outils** | socat, bash /dev/tcp, ou netcat |
| **Fréquence** | Uniquement pendant tests |
| **Alternative production** | Python socket natif (pas bash) |

---

## 🔑 Conclusion

**`socket_client.sh` est:**
- ✅ Un script **UTILITAIRE DE TEST** 
- ✅ Appelé par `test_socket_communication.sh`
- ✅ Fourni dans la documentation de tests
- ❌ **PAS** exécuté en production
- ❌ **PAS** appelé par le code Python principal

**Il sert à valider** que le serveur socket TCP fonctionne correctement avant déploiement.
