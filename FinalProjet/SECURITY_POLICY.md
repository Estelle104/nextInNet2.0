# 🔒 Politique de Sécurité - FinalProjet

## Vue d'ensemble

Ce document décrit comment le système gère les **machines autorisées** vs **machines inconnues**.

---

## 📊 Tableau des accès

| Situation | Réception IP | Notification | SSH | Réseau |
|-----------|-------------|--------------|-----|--------|
| **Machine autorisée** (dans devices.conf) | ✓ IP fixe (ex: .100) | 🔵 INFO | ✓ Autorisé | ✓ Actif |
| **Machine inconnue** (IP dynamique) | ✓ IP dynamique (150-200) | 🟠 WARNING | ❌ BLOQUÉE | ❌ Expulsion |
| **IP bloquée** (dans blocked_ips.conf) | ❌ Pas d'IP | 🔴 BLOCKED | ❌ Refusée | ❌ Blacklistée |

---

## 🔌 Allocation des IPs

### Machine AUTORISÉE
```
MAC: AA:BB:CC:DD:EE:FF (dans devices.conf)
       ↓
DHCP Server reçoit DISCOVER
       ↓
Cherche MAC dans devices.conf
       ↓
✓ Trouvée → IP FIXE attribuée (ex: 192.168.43.100)
       ↓
Notification: ✓ [INFO] Appareil autorisé MAC=... IP=...
```

### Machine INCONNUE
```
MAC: 11:22:33:44:55:66 (NOT dans devices.conf)
       ↓
DHCP Server reçoit DISCOVER
       ↓
Cherche MAC dans devices.conf
       ↓
✗ Pas trouvée → IP DYNAMIQUE attribuée (ex: 192.168.43.150)
       ↓
Notification: ⚠️ [WARNING] Appareil inconnue MAC=... IP=...
```

---

## 🛡️ Règles SSH

### SSH depuis AUTORISÉE ✓
```
Machine autorisée (ex: 192.168.43.100) envoie SSH
       ↓
TCP Server détecte SSH
       ↓
Vérifie si IP autorisée → OUI
       ↓
✓ SSH ACCEPTÉ
       ↓
Notification: ✓ [INFO] SSH autorisé depuis machine connue
       ↓
Log: "SSH accepté depuis 192.168.43.100"
```

### SSH depuis INCONNUE ❌
```
Machine inconnue (ex: 192.168.43.150) envoie SSH
       ↓
TCP Server détecte SSH
       ↓
Vérifie si IP autorisée → NON
       ↓
✗ SSH REFUSÉ
       ↓
block_ip(192.168.43.150)
       ├─ Ajout dans blocked_ips.conf
       └─ Exécute: sudo iptables -I INPUT -s 192.168.43.150 -j DROP
       ├─ Exécute: sudo iptables -I FORWARD -s 192.168.43.150 -j DROP
       ↓
Notification: 🚫 [BLOCKED] TENTATIVE SSH MACHINE INCONNUE: 192.168.43.150 - EXPULSÉE
       ↓
⚠️ IP EXPULSÉE DU RÉSEAU (immédiatement)
```

---

## 📋 Configuration des appareils autorisés

### Ajouter une machine autorisée

**Fichier**: `backend/config/devices.conf`
```
# Format: MAC_ADDRESS|IP_ADDRESS
AA:BB:CC:DD:EE:FF|192.168.43.100
D0:C5:D3:8C:09:1D|192.168.43.200
1C:BF:CE:F1:F1:12|192.168.43.111
```

**Méthode 1**: Interface GUI
1. Ouvrir l'application
2. Aller à "Créer utilisateur" (device)
3. Entrer MAC et IP
4. Valider → Ajout automatique

**Méthode 2**: Éditer directement
```bash
echo "AA:BB:CC:DD:EE:99|192.168.43.150" >> backend/config/devices.conf
```

---

## 🔧 Pools d'IPs

### Distribution des adresses

```
192.168.43.0-99      → Réservées (serveur, interfaces)
192.168.43.100-149   → AUTORISÉES (IP fixes from devices.conf)
192.168.43.150-200   → INCONNUES (IP dynamiques)
192.168.43.201-255   → Réservées (broadcast, etc)
```

---

## 📢 Notifications en temps réel

### Interface notifications affiche:

#### 🔵 INFO (Bleu)
```
[12:34:56] [INFO] ✓ Appareil autorisé: MAC=AA:BB:CC:DD:EE:FF IP=192.168.43.100
```

#### 🟠 WARNING (Orange)
```
[12:35:00] [WARNING] ⚠️ Appareil inconnue: MAC=11:22:33:44:55:66 IP=192.168.43.150
[12:35:02] [WARNING] ⚠️ Machine INCONNUE DÉTECTÉE: 192.168.43.150:5050
```

#### 🔴 BLOCKED (Rouge)
```
[12:35:05] [BLOCKED] 🚫 TENTATIVE SSH MACHINE INCONNUE: 192.168.43.150 - BLOQUÉE & EXPULSÉE!
[12:35:05] [BLOCKED] 🚫 IP bloquée 192.168.43.150 refusée
```

---

## 🚨 Actions d'expulsion

### Quand une inconnue essaie SSH:

1. **TCP Server détecte SSH**
   - Analyse le contenu (cherche "ssh", "SSH", "OpenSSH", port 22)

2. **Blocage IP immédiat**
   ```bash
   sudo iptables -I INPUT -s <IP> -j DROP
   sudo iptables -I FORWARD -s <IP> -j DROP
   ```

3. **Enregistrement dans blocked_ips.conf**
   ```
   192.168.43.150
   ```

4. **Notification alerte**
   ```
   🚫 TENTATIVE SSH MACHINE INCONNUE: 192.168.43.150 - BLOQUÉE & EXPULSÉE!
   ```

5. **Résultat**: IP complètement coupée du réseau

---

## 📁 Fichiers concernés

| Fichier | Rôle | Modifié? |
|---------|------|----------|
| `backend/config/devices.conf` | Machines autorisées | - |
| `backend/config/blocked_ips.conf` | IPs expulsées | ✓ Auto |
| `backend/config/dhcp_leases.conf` | Locations DHCP | ✓ Auto |
| `backend/logs/notifications.log` | Alertes sécurité | ✓ Auto |
| `backend/logs/Connexion.log` | Logs connexions | ✓ Auto |
| `backend/serveur/dhcp_server.py` | Allocation IPs | ✓ Modifié |
| `backend/serveur/tcp_server_simple.py` | Détection SSH | ✓ Modifié |

---

## ✅ Changements implémentés

### DHCP Server (`dhcp_server.py`)

**Avant**:
- Machines inconnues → Pas d'IP

**Après**:
- ✓ Machines autorisées → IP fixe (from devices.conf)
- ✓ Machines inconnues → IP dynamique (150-200)
- ✓ Nouvelle fonction `find_free_dynamic_ip()` pour le pool

### TCP Server (`tcp_server_simple.py`)

**Avant**:
- SSH bloqué mais pas expulsé
- Pas de distinction autorisée vs inconnue

**Après**:
- ✓ Nouvelle fonction `detect_is_device_authorized()` 
- ✓ SSH autorisé pour appareils dans devices.conf
- ✓ SSH BLOQUÉ pour inconnues + expulsion iptables
- ✓ Meilleure détection SSH (cherche "ssh", "SSH", "OpenSSH", port 22)
- ✓ Import subprocess pour exécuter iptables

---

## 🧪 Test du système

### Test 1: Machine autorisée reçoit IP fixe
```bash
# Ajouter dans devices.conf
echo "AA:BB:CC:DD:EE:01|192.168.43.100" >> backend/config/devices.conf

# Se connecter avec cette MAC
# Résultat attendu: Reçoit 192.168.43.100
```

### Test 2: Machine inconnue reçoit IP dynamique
```bash
# Se connecter avec MAC NOT dans devices.conf
# Résultat attendu: 
#   - Reçoit IP de 150-200
#   - Notification WARNING apparaît
```

### Test 3: SSH sur inconnue = expulsion
```bash
# Depuis machine inconnue (150-200):
ssh admin@192.168.43.1

# Résultat attendu:
#   - Connexion SSH refusée
#   - Notification BLOCKED: "TENTATIVE SSH BLOQUÉE"
#   - IP expulsée avec iptables
#   - sudo iptables -L affiche la règle DROP
```

### Test 4: SSH sur autorisée = OK
```bash
# Depuis machine autorisée (ex: 100):
ssh admin@192.168.43.1

# Résultat attendu:
#   - SSH accepté
#   - Notification INFO: "SSH autorisé depuis machine connue"
#   - Connexion établie normalement
```

---

## ⚙️ Prérequis

### Sudo sans mot de passe pour iptables (optionnel mais recommandé)

Pour éviter de rentrer le mot de passe à chaque fois:

```bash
sudo visudo

# Ajouter cette ligne (remplacer andry par votre user):
andry ALL=(ALL) NOPASSWD: /usr/sbin/iptables
```

### Sinon

Le système demandera `sudo` à chaque blocage iptables (moins critique car asynchrone).

---

## 📊 Flux complet du système

```
┌────────────────────────────────────────────────────────────┐
│                  Appareil se connecte                       │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────────┐
        │  DHCP DISCOVER (port 67)   │
        └────────────────┬───────────┘
                         │
         ┌───────────────┴───────────────┐
         ↓                               ↓
   ✓ MAC autorisée            ❌ MAC inconnue
         │                               │
         ↓                               ↓
   IP FIXE                        IP DYNAMIQUE
  (100-149)                       (150-200)
         │                               │
         ↓                               ↓
  Notif: INFO                    Notif: WARNING
         │                               │
         └───────────────┬───────────────┘
                         ↓
              ┌─────────────────────────┐
              │ Appareil utilise réseau │
              └────────────┬────────────┘
                           │
                    ┌──────┴──────┐
                    ↓             ↓
              SSH attempt    Autres connexions
                    │             │
         ┌──────────┴─────┐       │
         ↓                ↓       ↓
    Autorisée        Inconnue   Autorisée
         │                ↓       │
         ↓         ┌─────────┐   ↓
    ✓ SSH OK      │ BLOQUER │  ✓ OK
                  │ & EXPULSER
                  └─────────┘
```

---

## 🔔 Badges dans l'interface

| Badge | Couleur | Signification |
|-------|---------|--------------|
| 🔔 | Bleu | 0 alerte (tout OK) |
| 🔔 | Orange | Appareils inconnues détectés |
| 🔔 | Rouge | Tentatives suspectes bloquées |

---

**Version**: 2.0  
**Date**: 21 janvier 2026  
**Statut**: Système de sécurité complet implémenté
