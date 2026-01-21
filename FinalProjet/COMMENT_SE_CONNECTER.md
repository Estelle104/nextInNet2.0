# 🚀 LANCER TOUT LE SYSTÈME EN UNE SEULE COMMANDE

## ⚡ Procédure Rapide

Ouvrez UN SEUL terminal et lancez :

```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet
sudo ./start_system.sh
```

**C'est tout !** Cela va :
1. ✅ Configurer l'interface WiFi
2. ✅ Lancer le Point d'Accès WiFi (hostapd)
3. ✅ Lancer le serveur DHCP
4. ✅ Lancer le serveur TCP de sécurité
5. ✅ Afficher les informations

Le script restera actif et monitora les services. Appuyez sur **Ctrl+C** pour arrêter.

---

## 📡 Réseau WiFi Disponible

**Après lancement, les autres machines verront :**
- **SSID:** `NextInNet-Secure`
- **Mot de passe:** `SecureNetwork123`
- **IP gateway:** `192.168.43.1`
- **Pool DHCP:** `192.168.43.100-200`

---

## 🔓 Se Connecter depuis une Autre Machine

### Étape 1: Trouver le WiFi
Cherchez `NextInNet-Secure` dans les réseaux disponibles

### Étape 2: Se Connecter
- Mot de passe: `SecureNetwork123`
- Attendez la connexion...

### Étape 3: Obtenir une IP
La machine recevra automatiquement une IP du DHCP (ex: `192.168.43.110`)

---

## 📊 Voir les Connexions

**Dans des terminaux séparés (après lancement):**

```bash
# Voir les IPs assignées par DHCP
tail -f /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/logs/dhcp.log

# Voir les connexions TCP et sécurité
tail -f /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/logs/tcp.log

# Voir les notifications de sécurité (alertes)
tail -f /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/logs/notifications.log
```

---

## 🔒 Système de Sécurité

| Machine | Statut | Logs |
|---------|--------|------|
| **Dans devices.conf** | ✅ Autorisée (sans limite) | INFO (vert) |
| **Inconnue (< 30s)** | ⏱️ Temporaire | WARNING (orange) |
| **Inconnue (> 30s)** | ❌ Déconnectée | TIMEOUT (rouge) |
| **Tentative SSH** | 🚫 Bloquée immédiatement | BLOCKED (rouge) |

---

## 📝 Enregistrer une Machine Comme Autorisée

1. **Regarder les logs DHCP** pour voir la MAC :
   ```bash
   tail -f backend/logs/dhcp.log
   # Voir: "⚠️ IP assignée (INCONNUE): 4E:E0:B8:0F:09:78"
   ```

2. **Ajouter dans `backend/config/devices.conf` :**
   ```bash
   nano backend/config/devices.conf
   # Ajouter:
   # 4E:E0:B8:0F:09:78|192.168.43.110|Mon_Laptop
   ```

3. **Redémarrer :**
   ```bash
   # Ctrl+C pour arrêter le script
   sudo ./start_system.sh
   ```

---

# 🌐 Informations de Votre PC

## 📍 Détails

### Adresses IP
- **WiFi (wlo1):** 192.168.43.1 (Point d'Accès)
- **Hostname:** mailb

### MAC Address
- **wlo1:** d8:43:ae:80:5c:c9

---

## ⚙️ Configuration
```bash
# Sur la machine cliente
echo "realtime 5" | nc 192.168.43.1 5050
```

---

## 🎯 Étapes Complètes pour Connecter une Autre Machine

### Côté VOTRE PC (mailb)

#### Étape 1️⃣: Configurer le point d'accès
```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet

./configure_ap.sh
# Choisir l'interface wlan0
# Configurer IP: 192.168.43.1
```

#### Étape 2️⃣: Ajouter les MAC des appareils
```bash
nano backend/config/devices.conf

# Ajouter chaque appareil avec sa MAC:
# Format: MAC|IP|NOM
AA:BB:CC:DD:EE:FF|192.168.43.100|Appareil_1
D0:C5:D3:8C:09:1D|192.168.43.101|Appareil_2
```

#### Étape 3️⃣: Lancer le système
```bash
./start_system.sh
# Choisir option 1 (DHCP + TCP + GUI)
```

### Côté AUTRE MACHINE (Cliente)

#### Étape 1️⃣: Se connecter au réseau
```bash
# Option A: Manuellement
sudo ip link set wlan0 up
sudo dhclient wlan0

# Option B: Dans les paramètres WiFi
# Chercher le réseau: "192.168.43.0" ou chercher "mailb"
```

#### Étape 2️⃣: Vérifier la connexion
```bash
# Vérifier que vous avez une IP
ip addr show wlan0
# Vous devez voir: 192.168.43.100+ (ou autre dans le pool)

# Tester la connexion
ping 192.168.43.1
echo "realtime 5" | nc 192.168.43.1 5050
```

---

## 📋 Résumé des Adresses

### Pour les Autres Machines (Clients)

| Information | Valeur |
|-------------|--------|
| **Nom du Point d'Accès** | mailb / mailb.andry.local |
| **IP du Serveur** | 192.168.43.1 |
| **Réseau** | 192.168.43.0/24 |
| **Port TCP** | 5050 |
| **Port DHCP** | 67/UDP (automatique) |

### Commandes pour les Clients

```bash
# Se connecter au réseau DHCP
sudo dhclient wlan0

# Tester la connexion
ping 192.168.43.1

# Récupérer les logs
echo "realtime 5" | nc 192.168.43.1 5050

# Vérifier l'IP assignée
ip addr show wlan0
```

---

## 🔐 Configuration DHCP Automatique

Une fois que vous lancez le système:

```
Machine Cliente
    ↓ DHCP DISCOVER (envoie sa MAC)
Serveur DHCP sur 192.168.43.1
    ↓ Cherche la MAC dans devices.conf
    ├─ ✓ MAC autorisée → DHCP OFFER + ACK
    │  └─ Cliente reçoit IP: 192.168.43.100+ et peut se connecter
    │
    └─ ✗ MAC inconnue → Pas de réponse
       └─ Cliente n'obtient pas d'IP
```

---

## 📱 Exemples Concrets

### Exemple 1: PC Portable Connecté au Point d'Accès

**Votre PC (mailb):**
- Gateway: 192.168.43.1
- MAC: d8:43:ae:80:5c:c9
- Serveur DHCP: Port 67
- Serveur TCP: Port 5050

**Portable Cliente:**
```bash
# 1. MAC du portable: AA:BB:CC:DD:EE:FF
# 2. Ajouter dans devices.conf
# 3. Se connecter au réseau
sudo dhclient wlan0
# 4. Reçoit IP: 192.168.43.100
# 5. Peut maintenant accéder à:
#    - Serveur TCP: 192.168.43.1:5050
#    - Fichiers partagés (futur)
```

### Exemple 2: Smartphone Connecté

**Smartphone:**
1. Chercher les réseaux WiFi
2. Se connecter au SSID "192.168.43.x" (ou le nom du réseau)
3. Recevoir une IP du DHCP
4. Accéder aux services sur 192.168.43.1

---

## 🛠️ Dépannage

### "Je n'arrive pas à me connecter"

```bash
# Vérifier que DHCP est actif
sudo lsof -i :67

# Vérifier votre MAC est dans devices.conf
cat backend/config/devices.conf

# Vérifier que votre interface est active
ip link show wlan0

# Forcer le renouvellement DHCP
sudo dhclient -r wlan0
sudo dhclient wlan0
```

### "Je reçois pas d'IP"

1. **Vérifier la MAC est autorisée:**
   ```bash
   cat backend/config/devices.conf | grep MA_MAC
   ```

2. **Ajouter votre MAC s'il manque:**
   ```bash
   echo "MA:CA:AD:DR:ES:SE|192.168.43.110|Mon_Appareil" >> \
     backend/config/devices.conf
   ```

3. **Relancer DHCP** (il recharge auto)

### "Connexion TCP refusée"

```bash
# Vérifier que TCP serveur est actif
sudo lsof -i :5050

# Tester la connexion
echo "realtime 5" | nc 192.168.43.1 5050

# Si refusée: vérifier les alertes
cat backend/logs/notifications.log
```

---

## 📊 Vue d'Ensemble Réseau

```
                    VOTRE PC (mailb)
                    192.168.43.1
                    ┌─────────────┐
                    │ Serveur     │
                    │ DHCP + TCP  │
                    │ + GUI       │
                    └─────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │  Appareil 1 │ │  Appareil 2 │ │  Appareil N │
    │ 192.168.43. │ │ 192.168.43. │ │ 192.168.43. │
    │    100      │ │    101      │ │    102      │
    └─────────────┘ └─────────────┘ └─────────────┘
```

---

## ✅ Checklist Connexion Réseau

- [ ] Votre PC a l'IP: 192.168.43.1
- [ ] DHCP est actif (port 67)
- [ ] TCP serveur est actif (port 5050)
- [ ] Les MACs des autres machines sont dans devices.conf
- [ ] Les autres machines peuvent faire DHCP et reçoivent une IP
- [ ] Les autres machines peuvent atteindre 192.168.43.1:5050
- [ ] Dashboard affiche les connexions

---

**Votre PC est prêt à accepter des connexions!** 🎉

Créé: 20 janvier 2026
