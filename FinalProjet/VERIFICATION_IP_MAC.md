# 🔍 Vérification IP/MAC - Guide Complet

## 📍 OÙ SE TROUVENT LES CODES ?

### 1️⃣ Fichier Principal : `backend/serveur/tcp_server_simple.py`

#### 🔹 Ligne 17 : Chemin du fichier de configuration
```python
DEVICES_FILE = "/home/andry/.../backend/config/devices.conf"
```

#### 🔹 Lignes 26-38 : Fonction `load_devices()` - Charge les machines autorisées
```python
def load_devices():
    """Charge la liste des appareils autorisés depuis devices.conf"""
    devices = {}
    try:
        if os.path.exists(DEVICES_FILE):
            with open(DEVICES_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('|')
                        if len(parts) == 2:
                            ip, mac = parts[0].strip(), parts[1].strip()
                            devices[ip] = mac    # Stocke {IP: MAC}
    except Exception as e:
        print(f"✗ Erreur chargement devices: {e}")
    return devices
```

**Ce que ça fait :**
- Ouvre le fichier `devices.conf`
- Lit chaque ligne (format : `IP|MAC`)
- Crée un dictionnaire : `{"192.168.1.100": "AA:BB:CC:DD:EE:FF", ...}`
- Retourne ce dictionnaire

#### 🔹 Lignes 57-60 : Fonction `is_device_known()` - Vérifie si une IP est connue
```python
def is_device_known(ip):
    """Vérifie si l'IP est enregistrée dans devices.conf"""
    devices = load_devices()
    return ip in devices    # True si IP trouvée, False sinon
```

**Ce que ça fait :**
- Appelle `load_devices()` pour récupérer la liste
- Vérifie si l'IP passée en paramètre existe dans le dictionnaire
- Retourne `True` (autorisée) ou `False` (inconnue/bloquée)

#### 🔹 Ligne 134 : Utilisation dans la vérification de sécurité
```python
if not is_device_known(ip):
    # Machine inconnue détectée
    # → Crée une notification
    # → Lance le timer de 1 minute
    # → Si tentative SSH : bloque immédiatement
```

---

## 📁 OÙ SONT LES FICHIERS DE CONFIGURATION ?

### 📌 Fichier Principal : `backend/config/devices.conf`

**Emplacement complet :**
```
/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/config/devices.conf
```

**Format du fichier :**
```properties
# Commentaires (commencent par #)
# Format: IP_ADDRESS|MAC_ADDRESS

192.168.1.100|AA:BB:CC:DD:EE:FF
192.168.1.101|AA:BB:CC:DD:EE:01
192.168.1.102|AA:BB:CC:DD:EE:02
192.168.1.105|AA:BB:CC:DD:EE:05
```

**Exemple de contenu actuel :**
```
# 5 machines autorisées
# Format: IP|MAC

192.168.1.100|AA:BB:CC:DD:EE:FF  ← Autorisée
192.168.1.101|AA:BB:CC:DD:EE:01  ← Autorisée
192.168.1.102|AA:BB:CC:DD:EE:02  ← Autorisée
192.168.1.105|AA:BB:CC:DD:EE:05  ← Autorisée
192.168.1.8|AA:BB:CC:DD:EE:GG    ← Autorisée
```

---

## 🔴 FICHIER DES MACHINES BLOQUÉES

**Emplacement :**
```
backend/config/blocked_ips.conf
```

**Contenu (rempli automatiquement) :**
```
# IPs bloquées automatiquement après tentative SSH
192.168.1.200
192.168.1.250
```

---

## 🔄 FLUX DE VÉRIFICATION COMPLET

```
Machine X (IP: 192.168.1.200) se connecte
        ↓
handle_client() appelée
        ↓
check_and_handle_unknown(192.168.1.200, ..., request)
        ↓
is_device_known(192.168.1.200) appelée
        ↓
load_devices() charge devices.conf
        ↓
Cherche "192.168.1.200" dans le dictionnaire
        ↓
❌ TROUVÉE ? Non !
        ↓
Status = "UNKNOWN"
        ↓
✓ Notification créée
✓ Log enregistré [UNKNOWN]
✓ Timer 1 minute activé
        ↓
Si elle essaie SSH:
  → Status = "BLOCKED"
  → IP ajoutée à blocked_ips.conf
  → Connexion rejetée
```

---

## ✏️ COMMENT AJOUTER UNE MACHINE AUTORISÉE ?

### Méthode 1 : Éditer directement le fichier
```bash
# Ajouter manuellement une ligne
echo "192.168.1.200|CC:DD:EE:FF:AA:BB" >> backend/config/devices.conf
```

### Méthode 2 : Utiliser nano/vim
```bash
nano backend/config/devices.conf
# Ajouter : 192.168.1.200|CC:DD:EE:FF:AA:BB
# Ctrl+O (save), Ctrl+X (exit)
```

### Important : Format obligatoire
```
IP|MAC

Bon:   192.168.1.200|AA:BB:CC:DD:EE:FF
Mauvais: 192.168.1.200 AA:BB:CC:DD:EE:FF  (pas de |)
Mauvais: 192.168.1.200                     (pas de MAC)
```

---

## 🧪 TEST : Vérifier que la détection fonctionne

### Sur le serveur (après avoir lancé tcp_server_simple.py) :
```bash
# Depuis une autre machine INCONNUE du réseau
echo 'realtime 5' | nc 192.168.43.29 5050
```

### Résultat dans le serveur :
```
[UNKNOWN] Machine INCONNUE connectée: 192.168.1.200:XXXXX
⚠️ NOTIFICATION [WARNING]: 🔴 MACHINE INCONNUE: 192.168.1.200:XXXXX
```

---

## 📊 Résumé des Fichiers

| Fichier | Chemin | Contenu | Modifiable ? |
|---------|--------|---------|------------|
| **devices.conf** | backend/config/devices.conf | IPs/MACs autorisées | ✅ OUI |
| **blocked_ips.conf** | backend/config/blocked_ips.conf | IPs bloquées | ⚠️ Auto (SSH détecte) |
| **tcp_server_simple.py** | backend/serveur/tcp_server_simple.py | Code de vérification | ❌ Non (sauf modifs) |

---

**Tout est maintenant clair ? 🎯**
