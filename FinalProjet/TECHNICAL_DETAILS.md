# 🔧 Détails Techniques - Système DHCP+MAC+IP

## Architecture du Système

```
┌─────────────────────────────────────────────────────────┐
│                    VOTRE PC (Gateway)                    │
│                    192.168.43.1                          │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Serveur DHCP (Port 67/UDP)                       │   │
│  │ • Écoute les requêtes DHCP DISCOVER              │   │
│  │ • Extrait MAC adresse                            │   │
│  │ • Vérifie si MAC est dans devices.conf           │   │
│  │ • Assigne IP du pool (192.168.43.100-200)       │   │
│  │ • Envoie DHCP OFFER/ACK                         │   │
│  └──────────────────────────────────────────────────┘   │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Serveur TCP (Port 5050/TCP)                      │   │
│  │ • Reçoit connexions des clients                  │   │
│  │ • Vérifie MAC + IP correspondent                │   │
│  │ • Applique la sécurité (timeout, blocage)       │   │
│  │ • Enregistre les logs                            │   │
│  └──────────────────────────────────────────────────┘   │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Interface GUI (Client)                           │   │
│  │ • Affiche les connexions                         │   │
│  │ • Affiche les notifications                      │   │
│  │ • Rafraîchit chaque 2 secondes                  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         ↕  WiFi/Ethernet (Réseau 192.168.43.0/24)
┌─────────────────────────────────────────────────────────┐
│              MACHINES CLIENTES (Network)                 │
│                                                           │
│  Client 1 (MAC: AA:BB:CC:DD:EE:FF)                      │
│  ├─ DHCP Request → IP 192.168.43.100                    │
│  └─ TCP :5050 → Authorization ✓                         │
│                                                           │
│  Client 2 (MAC: D0:C5:D3:8C:09:1D)                      │
│  ├─ DHCP Request → IP 192.168.43.200                    │
│  └─ TCP :5050 → Authorization ✓                         │
│                                                           │
│  Attacker (MAC inconnue)                                 │
│  ├─ DHCP Request → ✗ NO RESPONSE                        │
│  └─ Pas d'accès au réseau                               │
└─────────────────────────────────────────────────────────┘
```

## Fichiers Clés

### 1. `backend/serveur/dhcp_server.py` (425 lignes)

**Responsabilités:**
- Écoute port 67 UDP
- Parse requêtes DHCP DISCOVER
- Charge liste des MAC autorisées
- Gère les leases DHCP (allocation d'IP)
- Enregistre les allocations dans dhcp_leases.conf

**Fonctions principales:**

```python
load_authorized_devices()      # Charge devices.conf
get_ip_for_mac(mac)           # Assigne ou récupère l'IP pour une MAC
build_dhcp_offer()            # Construit réponse DHCP OFFER
build_dhcp_ack()              # Construit réponse DHCP ACK
handle_dhcp_request()         # Traite une requête DHCP
start_dhcp_server()           # Boucle d'écoute principale
```

**Configuration:**
- Port: 67 (UDP)
- Réseau: 192.168.43.0/24
- Gateway: 192.168.43.1
- Pool d'IP: 192.168.43.100-200
- Lease time: 3600s (1 heure)

### 2. `backend/serveur/tcp_server_simple.py` (275 lignes)

**Responsabilités:**
- Écoute port 5050 TCP
- Reçoit les connexions des clients
- Vérifie MAC + IP
- Applique règles de sécurité
- Enregistre les logs

**Fonctions principales:**

```python
load_devices()                # Charge devices.conf (MAC -> IP mapping)
is_device_known(ip, mac)      # Vérifie si MAC|IP est autorisée
check_and_handle_unknown()    # Applique règles de sécurité
create_notification()         # Écrit les alertes
block_ip()                    # Ajoute à la liste noire
handle_client()               # Traite une connexion TCP
start_server()                # Boucle d'écoute principale
```

**Ports:**
- Écoute: 5050 TCP
- Accepte les commandes: "realtime [N]" ou "history"

### 3. `backend/config/devices.conf` (Configuration)

**Format:**
```
# MAC_ADDRESS|IP_ADDRESS|DEVICE_NAME
AA:BB:CC:DD:EE:FF|192.168.43.100|PC_Bureau
D0:C5:D3:8C:09:1D|192.168.43.200|Routeur
```

**Parsing:**
```python
devices = {}  # {MAC: IP_ADDRESS}
for line in file:
    mac = line.split('|')[0].upper()
    ip = line.split('|')[1]
    devices[mac] = ip
```

### 4. `backend/config/dhcp_leases.conf` (Auto-généré)

**Format:**
```
MAC|IP|EXPIRATION
AA:BB:CC:DD:EE:FF|192.168.43.100|2026-01-20T15:30:45.123456
```

**Généré par:** dhcp_server.py
**Utilisé par:** Reprendre les allocations après redémarrage

### 5. `backend/config/blocked_ips.conf` (Auto-généré)

**Format:**
```
192.168.43.150
192.168.43.151
```

**Généré par:** tcp_server_simple.py lors d'une tentative SSH
**Nettoyage:** Manuel (rm backend/config/blocked_ips.conf)

## Flux de Vérification Sécurité

### Phase 1: DHCP (Port 67)

```
1. Machine Cliente envoie DHCP DISCOVER
   └─ Contient: MAC address dans HWaddr

2. Serveur DHCP reçoit
   └─ Extrait MAC: parse(HWaddr) → "AA:BB:CC:DD:EE:FF"

3. Recherche MAC dans devices.conf
   ├─ Trouvé: 
   │  └─ Récupère IP assignée (192.168.43.100)
   │  └─ Envoie DHCP OFFER/ACK
   │  └─ Log: "✓ DHCP ACK: MAC -> IP"
   │
   └─ Pas trouvé:
      └─ Ignore (pas de réponse)
      └─ Log: "✗ MAC non autorisée"

4. Client reçoit (ou pas) l'IP
   └─ Si pas de réponse DHCP: Pas d'accès réseau
```

### Phase 2: TCP (Port 5050)

```
1. Machine Cliente connectée au réseau avec IP assignée
   ├─ IP: 192.168.43.100 (du DHCP)
   └─ MAC: AA:BB:CC:DD:EE:FF

2. Cliente envoie: "realtime 5"
   └─ Connexion TCP depuis (IP, Port) vers 5050

3. Serveur TCP reçoit
   ├─ IP Client: 192.168.43.100
   └─ Requête: "realtime 5"

4. Vérification: is_device_known(ip, mac=?)
   ├─ Si MAC fournie (futur):
   │  ├─ Cherche MAC dans devices
   │  └─ Vérifie: devices[MAC] == IP
   │
   └─ Sinon (actuel):
      └─ Cherche si IP existe dans devices.values()

5. Résultat:
   ├─ ✓ AUTHORIZED:
   │  ├─ Envoie les logs demandés
   │  └─ Log: "[INFO] Connexion autorisée"
   │
   ├─ ✗ UNKNOWN:
   │  ├─ Accepte temporairement (60s)
   │  └─ Log: "[WARNING] 🔴 MACHINE INCONNUE"
   │  └─ Notification: "MACHINE INCONNUE 192.168.43.150"
   │  └─ Si SSH detecté: block_ip() → BLOCKED
   │
   └─ ✗ BLOCKED (si IP bloquée):
      ├─ Rejette la connexion
      └─ Log: "[BLOCKED] Accès refusé"
```

## Protocole DHCP Simplifié

### Structure DHCP Packet

```
Bytes   Contenu
0       Message Type (1=REQUEST, 2=REPLY)
1       Hardware Type (1=Ethernet)
2       Hardware Address Length (6 for MAC)
3       Hops
4-7     Transaction ID (XID)
8-9     Seconds
10-11   Flags
12-15   Client IP
16-19   Your IP (assigné)
20-23   Server IP (DHCP Server)
24-27   Gateway IP
28-43   Client Hardware Address (MAC)
44-235  Server Hostname
236-239 Boot Filename
240+    DHCP Options (avec magic cookie 0x63825363)
```

### Options DHCP Utilisées

```
Option 1:  Subnet Mask (255.255.255.0)
Option 3:  Router/Gateway (192.168.43.1)
Option 6:  DNS Servers (8.8.8.8)
Option 51: Lease Time (3600 secondes)
Option 53: DHCP Message Type (2=OFFER, 5=ACK)
Option 54: DHCP Server Identifier
Option 255: End
```

## Matrices de Décision

### Vérification DHCP

| MAC dans devices.conf? | Action | Résultat |
|----------------------|--------|----------|
| ✓ Oui | Assigner IP | DHCP ACK → Client reçoit IP |
| ✗ Non | Ignorer | Pas de réponse → Pas d'IP |

### Vérification TCP

| IP dans devices? | MAC correct? | Action | Résultat |
|-----------------|-------------|--------|----------|
| ✓ Oui | ✓ Match | Autoriser | Accès complet |
| ✓ Oui | ✗ Mismatch | Warning | 60s timeout |
| ✗ Non | - | Bloquer | Rejet immédiat |
| - | - | SSH détecté | Ajouter à blacklist |

## Logs et Monitoring

### Log DHCP (`backend/logs/dhcp.log`)

```
[2026-01-20 15:30:45] 🚀 Serveur DHCP démarré sur port 67
[2026-01-20 15:30:45]    Réseau: 192.168.43.0/255.255.255.0
[2026-01-20 15:31:00] → DHCP Request de AA:BB:CC:DD:EE:FF
[2026-01-20 15:31:00] ✓ Lease sauvegardé: AA:BB:CC:DD:EE:FF -> 192.168.43.100
[2026-01-20 15:31:00] ✓ DHCP OFFER envoyé: AA:BB:CC:DD:EE:FF -> 192.168.43.100
[2026-01-20 15:31:00] ✓ DHCP ACK envoyé: AA:BB:CC:DD:EE:FF -> 192.168.43.100
```

### Log Connexion (`backend/logs/Connexion.log`)

```
[2026-01-20 15:31:00] [INFO] Client from 192.168.43.100:54321
[2026-01-20 15:31:05] [UNKNOWN] Machine INCONNUE connectée: 192.168.43.150:54322
[2026-01-20 15:32:05] [TIMEOUT] Machine inconnue DECONNECTEE (timeout 1min): 192.168.43.150
```

### Notifications Sécurité (`backend/logs/notifications.log`)

```
[2026-01-20 15:31:05] [WARNING] 🔴 MACHINE INCONNUE: 192.168.43.150:54322
[2026-01-20 15:31:10] [BLOCKED] 🚫 ATTAQUE SSH depuis 192.168.43.150 - BLOQUÉE
[2026-01-20 15:32:05] [TIMEOUT] ⏱️ TIMEOUT: Machine inconnue 192.168.43.150 déconnectée
```

## Performance et Limitations

### Capacités

- **Max clients simultanés:** ~100 (pool DHCP: 100-200)
- **Lease time:** 1 heure (configurable)
- **Timeout inconnues:** 60 secondes
- **Refresh GUI:** 2 secondes
- **Threads:** Un par connexion TCP

### Limitations

- ⚠️ DHCP simplifié (pas de RENEW, REBIND)
- ⚠️ Pas de contrôle WiFi (utiliser hostapd extérieur)
- ⚠️ MAC extraction du champ HWaddr dans requête DHCP
- ⚠️ IPs fixes = pas de DHCP dynamique vrai

### Améliorations Possibles

- [ ] Support vrai DHCP (RENEW, REBIND)
- [ ] Extraction MAC depuis TCP connection
- [ ] GUI d'ajout/suppression d'appareils
- [ ] Backup automatique des logs
- [ ] Support IPv6
- [ ] Statistiques temps réel

## Commandes de Diagnostic

```bash
# Vérifier les ports
sudo lsof -i :67,5050

# Voir les requêtes DHCP
sudo tcpdump -i eth0 'udp port 67'

# Voir les connexions TCP
sudo netstat -an | grep 5050

# Tracer une machine spécifique
sudo tcpdump -i eth0 'host 192.168.43.100'

# Tester DHCP manuellement
sudo dhclient -v eth0 (sur le client)

# Vérifier les allocations
cat backend/config/dhcp_leases.conf

# Monitor en temps réel
tail -f backend/logs/dhcp.log &
tail -f backend/logs/Connexion.log &
tail -f backend/logs/notifications.log
```

---

**Document technique complet** | Mise à jour: 20 janvier 2026
