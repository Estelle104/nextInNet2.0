# 🔐 Système de Sécurité Réseau DHCP+MAC+IP

## 📌 Résumé de la Configuration

Vous avez maintenant un **système complet de sécurité réseau** avec:

✅ **Serveur DHCP** - Assigne automatiquement les IPs  
✅ **Vérification MAC+IP** - Double vérification de sécurité  
✅ **Gestion d'accès** - Autorisation/Blocage par MAC  
✅ **Notifications en temps réel** - Alertes de sécurité  
✅ **Interface graphique** - Dashboard de monitoring  

---

## 🚀 Démarrage Rapide (3 étapes)

### Étape 1: Configurer votre PC comme point d'accès
```bash
./configure_ap.sh
# Sélectionner l'interface (eth0, wlan0, etc.)
```

### Étape 2: Ajouter les appareils autorisés

Éditer `backend/config/devices.conf`:
```properties
# Format: MAC|IP|NOM
AA:BB:CC:DD:EE:FF|192.168.43.100|Mon_Appareil
```

### Étape 3: Démarrer les services
```bash
./start_system.sh
# Choisir l'option 1 pour tout lancer
```

---

## 📁 Fichiers Importants

| Fichier | Rôle |
|---------|------|
| `backend/serveur/dhcp_server.py` | Serveur DHCP (port 67) |
| `backend/serveur/tcp_server_simple.py` | Serveur de sécurité (port 5050) |
| `backend/config/devices.conf` | Liste blanche (MAC \| IP \| NOM) |
| `backend/config/dhcp_leases.conf` | Allocations DHCP (auto-généré) |
| `backend/logs/dhcp.log` | Logs DHCP |
| `backend/logs/Connexion.log` | Logs de connexion |
| `backend/logs/notifications.log` | Logs de sécurité |

---

## 🔧 Configuration

### Format `devices.conf`

```
# MAC | IP Assignée | Nom Appareil
AA:BB:CC:DD:EE:FF|192.168.43.100|PC_Bureau
D0:C5:D3:8C:09:1D|192.168.43.200|Routeur
```

**Comment ajouter une machine:**

1. Obtenir la MAC:
```bash
# Sur la machine à ajouter
ifconfig  # chercher "HWaddr" ou "ether"
# ou
python3 backend/scripts/get_mac_address.py
```

2. Ajouter dans `devices.conf`
3. Redémarrer DHCP

---

## 📊 Flux de Sécurité

```
Cliente Machine
    ↓ DHCP DISCOVER
Serveur DHCP
    ↓ Vérifie si MAC est autorisée
    ├─ ✓ YES  → Assigne IP → DHCP OFFER/ACK
    └─ ✗ NO   → Pas de réponse → Pas d'IP
    ↓ Connexion réseau établie
Cliente utilise la nouvelle IP
    ↓ TCP Connect :5050
Serveur TCP
    ↓ Vérifie MAC + IP correspondent
    ├─ ✓ YES  → AUTHORIZED
    └─ ✗ NO   → WARNING + 60s timeout
    ↓
Dashboard GUI
    ├─ Affiche les alertes
    └─ Log tout dans notifications.log
```

---

## 🔒 Sécurité

### Vérification Double

1. **DHCP**: Seules les MAC autorisées reçoivent une IP
2. **TCP**: Vérifie que MAC + IP correspondent à la configuration

### Détection d'Attaque

- Tentative SSH → Blocage IP automatique
- Machine inconnue → Warning + 60s timeout
- IP bloquée → Rejet immédiat

### Logs de Sécurité

Consulter `backend/logs/notifications.log`:
```
[2026-01-20 15:31:05] [WARNING] 🔴 MACHINE INCONNUE: 192.168.43.150:54322
[2026-01-20 15:32:05] [BLOCKED] 🚫 ATTAQUE SSH depuis 192.168.43.150
```

---

## 📋 Commandes Utiles

### Obtenir les infos réseau
```bash
# Afficher toutes les interfaces
ip link show

# Obtenir la MAC de votre PC
python3 backend/scripts/get_mac_address.py

# Vérifier l'IP assignée
ip addr show
```

### Démarrer les services individuellement
```bash
# Serveur DHCP (nécessite sudo)
sudo python3 backend/serveur/dhcp_server.py

# Serveur TCP
python3 backend/serveur/tcp_server_simple.py

# Interface GUI
python3 backend/client/client.py
```

### Tester la connexion
```bash
# Depuis une autre machine du réseau
echo "realtime 5" | nc 192.168.43.1 5050
```

### Nettoyer les logs
```bash
rm backend/logs/*.log
```

---

## 📖 Documentation Complète

Pour plus de détails, lire: **`GUIDE_DHCP_MAC_IP.md`**

Contient:
- Configuration avancée
- Dépannage
- Gestion de la sécurité
- Architecture complète

---

## ✨ Exemple Complet

### Configuration Initiale
```bash
# 1. Configurer le point d'accès
./configure_ap.sh
# Choisir wlan0

# 2. Éditer devices.conf avec vos appareils
nano backend/config/devices.conf
# Ajouter vos appareils avec leurs MAC

# 3. Démarrer le système
./start_system.sh
# Choisir option 1
```

### Résultat
- ✅ Serveur DHCP active (port 67)
- ✅ Serveur TCP de sécurité active (port 5050)
- ✅ GUI affiche les connexions et alertes
- ✅ Logs en temps réel

---

## 🐛 Si ça ne marche pas

### DHCP ne démarre pas
```bash
# Erreur "Address already in use"
sudo lsof -i :67
sudo kill -9 <PID>

# Relancer avec sudo
sudo python3 backend/serveur/dhcp_server.py
```

### Clients n'obtiennent pas d'IP
```bash
# Vérifier DHCP écoute
sudo netstat -udp | grep 67

# Vérifier MAC est autorisée
cat backend/config/devices.conf

# Voir les logs DHCP
tail -50 backend/logs/dhcp.log
```

### Connexion refusée
```
Raison possible: MAC inconnue ou pas dans devices.conf

Solution: 
1. Ajouter la MAC dans devices.conf
2. Relancer DHCP
```

---

## 📞 Support

Fichiers pour diagnostiquer les problèmes:
- `backend/logs/dhcp.log` - Logs du serveur DHCP
- `backend/logs/Connexion.log` - Logs de connexion TCP
- `backend/logs/notifications.log` - Alerts de sécurité

Exemples de commandes de debug:
```bash
# Voir les 20 dernières lignes du log DHCP
tail -20 backend/logs/dhcp.log

# Voir tout les alertes de sécurité
cat backend/logs/notifications.log

# Vérifier le format de devices.conf
grep -v "^#" backend/config/devices.conf
```

---

**Système prêt à l'emploi!** 🎉
