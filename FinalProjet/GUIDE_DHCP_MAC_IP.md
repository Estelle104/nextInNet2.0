# Guide Complet: Configuration du Serveur DHCP et Vérification MAC+IP

## 📋 Vue d'ensemble

Vous avez maintenant un système complet où:
1. **Votre PC** agit comme serveur DHCP (point d'accès)
2. **Les machines clientes** reçoivent automatiquement une IP via DHCP
3. **La vérification de sécurité** utilise **MAC + IP** pour autoriser/bloquer les appareils

## 🛠️ Configuration Requise

### 1. Configuration du Point d'Accès (AP)

Votre PC doit avoir:
- Une interface réseau configurée en mode AP (Access Point)
- IP: `192.168.43.1` (gateway/serveur)
- Réseau: `192.168.43.0/24`

```bash
# Exemple pour wlan0
sudo ip addr add 192.168.43.1/24 dev wlan0
sudo ip link set wlan0 up

# Vérifier:
ip addr show wlan0
```

### 2. Liste des Appareils Autorisés

**Fichier:** `backend/config/devices.conf`

**Format:** `MAC_ADDRESS|IP_ADDRESS|NOM_APPAREIL`

```properties
# Configuration des Appareils Autorisés
# Les IPs sont assignées par le serveur DHCP

AA:BB:CC:DD:EE:FF|192.168.43.100|PC_Bureau
AA:BB:CC:DD:EE:01|192.168.43.101|Laptop_1
D0:C5:D3:8C:09:1D|192.168.43.200|Routeur
```

**Comment ajouter une nouvelle machine:**
1. Obtenir sa MAC adresse: `ifconfig` ou `ip link show`
2. Ajouter une ligne: `MAC|IP_SOUHAITÉE|NOM`
3. Redémarrer le serveur DHCP

## 🚀 Démarrage des Services

### Étape 1: Démarrer le serveur DHCP

```bash
# Port 67 UDP (nécessite root/sudo)
sudo python3 backend/serveur/dhcp_server.py
```

**Résultat attendu:**
```
🚀 Serveur DHCP démarré sur port 67
   Réseau: 192.168.43.0/255.255.255.0
   Gateway: 192.168.43.1
   Pool: 192.168.43.100-200
```

### Étape 2: Démarrer le serveur de sécurité (TCP)

```bash
# Dans un autre terminal
python3 backend/serveur/tcp_server_simple.py
```

**Résultat attendu:**
```
✓ Serveur démarré sur 0.0.0.0:5050
✓ Logs: backend/logs/Connexion.log
```

### Étape 3: Démarrer l'interface graphique

```bash
# Dans un troisième terminal
python3 backend/client/client.py
```

## 📊 Flux de Vérification Sécurité

```
1. Machine cliente envoie DHCP DISCOVER
            ↓
2. Serveur DHCP extrait la MAC
            ↓
3. Vérifie si MAC est dans devices.conf
            ├─ ✓ OUI → Assigne l'IP → AUTHORIZED
            └─ ✗ NON → REJECTED (pas d'IP)
            ↓
4. Machine connectée avec (MAC, IP)
            ↓
5. Tentative de connexion TCP:5050
            ↓
6. Serveur TCP vérifie MAC + IP correspondent
            ├─ ✓ OUI → AUTHORIZED
            ├─ ✗ NON (IP différente) → WARNING + 60s timeout
            └─ ✗ NON (MAC inconnue) → BLOCKED
```

## 🔧 Fichiers de Configuration

### `devices.conf` - Liste blanche des appareils

```properties
# MAC|IP|NOM
AA:BB:CC:DD:EE:FF|192.168.43.100|PC_Bureau
```

**Champs:**
- `MAC`: Adresse MAC unique de la machine (format: `XX:XX:XX:XX:XX:XX`)
- `IP`: IP à assigner par DHCP (doit être dans pool `192.168.43.100-200`)
- `NOM`: Description de l'appareil (optionnel)

### `dhcp_leases.conf` - Allocations DHCP actives

```properties
AA:BB:CC:DD:EE:FF|192.168.43.100|2026-01-20T15:30:45.123456
```

**Auto-généré par le serveur DHCP**
- Enregistre qui a reçu quelle IP
- Expiration après 1 heure

### `blocked_ips.conf` - IPs bloquées après attaque

```
192.168.43.150
192.168.43.151
```

**Auto-généré** quand une tentative SSH ou attaque est détectée

## 📈 Logs et Monitoring

### Logs DHCP

**Fichier:** `backend/logs/dhcp.log`

```
[2026-01-20 15:30:45] → DHCP Request de AA:BB:CC:DD:EE:FF
[2026-01-20 15:30:45] ✓ DHCP OFFER envoyé: AA:BB:CC:DD:EE:FF -> 192.168.43.100
[2026-01-20 15:30:45] ✓ DHCP ACK envoyé: AA:BB:CC:DD:EE:FF -> 192.168.43.100
```

### Logs de Connexion

**Fichier:** `backend/logs/Connexion.log`

```
[2026-01-20 15:31:00] [INFO] Client from 192.168.43.100:54321
[2026-01-20 15:31:05] [UNKNOWN] Machine INCONNUE connectée: 192.168.43.150:54322
```

### Notifications de Sécurité

**Fichier:** `backend/logs/notifications.log`

```
[2026-01-20 15:31:05] [WARNING] 🔴 MACHINE INCONNUE: 192.168.43.150:54322
[2026-01-20 15:32:05] [TIMEOUT] ⏱️ TIMEOUT: Machine inconnue 192.168.43.150 déconnectée
```

## ✅ Tester le Système

### Test Local (Même PC)

```bash
# Terminal 1: Démarrer DHCP
sudo python3 backend/serveur/dhcp_server.py

# Terminal 2: Démarrer TCP Server
python3 backend/serveur/tcp_server_simple.py

# Terminal 3: Test
echo "realtime 5" | nc 127.0.0.1 5050
```

### Test Distant (Autre PC sur le réseau)

1. **Configurer autre PC sur le réseau WiFi/Eth**
   ```bash
   # Sur la machine cliente
   sudo dhclient wlan0  # ou eth0
   # Devrait recevoir une IP de votre DHCP
   ```

2. **Vérifier l'IP reçue**
   ```bash
   ip addr show  # ou ifconfig
   # Devrait être dans 192.168.43.100-200
   ```

3. **Tester la connexion**
   ```bash
   echo "realtime 5" | nc 192.168.43.1 5050
   ```

4. **Vérifier les logs**
   - Si MAC est autorisée: ✓ Connexion acceptée
   - Si MAC inconnue: ⚠️ WARNING dans notifications.log

## 🔐 Gestion de la Sécurité

### Ajouter un Nouvel Appareil Autorisé

1. **Obtenir la MAC:**
   ```bash
   # Sur l'appareil
   ifconfig wlan0 | grep "HWaddr\|ether"
   # ou
   python3 backend/scripts/get_mac_address.py
   ```

2. **Ajouter dans devices.conf:**
   ```bash
   echo "A1:B2:C3:D4:E5:F6|192.168.43.110|Mon_Appareil" >> backend/config/devices.conf
   ```

3. **Redémarrer DHCP** (ou il rechargera automatiquement)

### Bloquer une Machine

```bash
# Ajouter dans blocked_ips.conf
echo "192.168.43.150" >> backend/config/blocked_ips.conf
```

### Nettoyer les Logs

```bash
# Supprimer et recréer
rm backend/logs/Connexion.log
rm backend/logs/notifications.log
rm backend/logs/dhcp.log
```

## 📝 Code Clé - Vérification MAC+IP

### `tcp_server_simple.py` - Fonction de Vérification

**Fichier:** `backend/serveur/tcp_server_simple.py`

```python
# Ligne 57-78: is_device_known(ip, mac=None)
def is_device_known(ip, mac=None):
    """Vérifie si la combinaison MAC|IP est enregistrée"""
    devices = load_devices()
    
    # Si MAC fournie, vérifier que MAC -> IP correspond
    if mac:
        mac_upper = mac.upper()
        if mac_upper in devices:
            expected_ip = devices[mac_upper]
            if expected_ip == ip:
                return True
            else:
                # MAC connue mais IP différente
                print(f"⚠️ MAC {mac} reconnue mais IP mismatch")
                return False
        return False
```

### `dhcp_server.py` - Assignation d'IP

**Fichier:** `backend/serveur/dhcp_server.py`

```python
# Ligne 138-156: get_ip_for_mac(mac)
def get_ip_for_mac(mac):
    """
    Retourne l'IP assignée pour une MAC
    Si pas de lease valide, assigne une nouvelle IP
    """
    # 1. Vérifier si MAC bloquée
    # 2. Vérifier si lease existant valide
    # 3. Vérifier si MAC est autorisée
    # 4. Assigner une IP libre du pool
```

## 🐛 Dépannage

### Le serveur DHCP ne démarre pas

```bash
# Erreur: "Address already in use"
# Solution:
sudo lsof -i :67
sudo kill -9 <PID>

# Ou nécessite root:
sudo python3 backend/serveur/dhcp_server.py
```

### Les clients n'obtiennent pas d'IP

```bash
# 1. Vérifier DHCP en écoute
sudo netstat -udp | grep 67

# 2. Vérifier MAC est dans devices.conf
cat backend/config/devices.conf

# 3. Vérifier les logs DHCP
tail -20 backend/logs/dhcp.log
```

### Connexion acceptée mais IP mismatch

```
⚠️ MAC AA:BB:CC:DD:EE:FF reconnue mais IP mismatch: attendu 192.168.43.100, reçu 192.168.43.150
```

**Raisons possibles:**
- Le client n'a pas reçu l'IP du DHCP
- Le client a une configuration IP statique
- Rechargement manuel des IPs

**Solution:**
```bash
# Forcer le renouvellement DHCP sur le client
sudo dhclient -r
sudo dhclient wlan0
```

## 📚 Architecture Complète

```
nextInNet2.0/
├── backend/
│   ├── serveur/
│   │   ├── dhcp_server.py          ← Serveur DHCP
│   │   ├── tcp_server_simple.py    ← Serveur TCP + Vérification
│   │   └── __pycache__/
│   ├── config/
│   │   ├── devices.conf            ← Liste blanche (MAC|IP|NOM)
│   │   ├── dhcp_leases.conf        ← Allocations DHCP (AUTO)
│   │   └── blocked_ips.conf        ← IPs bloquées (AUTO)
│   ├── logs/
│   │   ├── Connexion.log
│   │   ├── notifications.log
│   │   └── dhcp.log
│   ├── client/
│   │   └── client.py               ← Interface graphique
│   └── scripts/
│       └── get_mac_address.py      ← Utilitaire MAC
└── frontend/
    └── views/
        └── notifications_view.py   ← Affichage notifications
```

## ✨ Prochaines Étapes

1. ✅ Configurer le point d'accès WiFi/Ethernet
2. ✅ Ajouter toutes les MAC autorisées dans `devices.conf`
3. ✅ Démarrer DHCP + TCP + GUI
4. ✅ Tester avec des machines distantes
5. ✅ Monitorer les logs de sécurité

---

**Créé:** 20 janvier 2026
