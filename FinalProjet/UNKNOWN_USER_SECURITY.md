# 🔒 Gestion des Utilisateurs Inconnus et Tentatives SSH

## Vue d'ensemble

Ce document décrit le système automatisé de gestion des **utilisateurs inconnus** avec :
- **Expulsion automatique** après 15 secondes d'inactivité
- **Détection SSH** avec blocage immédiat
- **Ping + Shutdown** pour éteindre la machine de l'attaquant

---

## 📋 Règles de Sécurité

### 1️⃣ Utilisateur AUTORISÉ (dans devices.conf)

```
Machine AUTORISÉE
     ↓
MAC dans devices.conf
     ↓
✓ Connexion acceptée
✓ SSH autorisé
✓ Pas d'expulsion
✓ Notification INFO
```

**Exemple:**
```
MAC: AA:BB:CC:DD:EE:FF
     ↓
IP FIXE: 192.168.43.100
     ↓
Status: ✓ AUTHORIZED
```

---

### 2️⃣ Utilisateur INCONNU (IP dynamique 150-200)

```
Machine INCONNUE
     ↓
IP dynamique attribuée (150-200)
     ↓
⏱️ Countdown 15 secondes
     ↓
├─ SI INACTIF 15s → ❌ EXPULSION AUTOMATIQUE
│  └─ iptables DROP + blocked_ips.conf
│
└─ SI TENTE SSH → 🚫 BLOCAGE IMMÉDIAT
   └─ PING + SHUTDOWN -h now
   └─ iptables DROP + blocked_ips.conf
```

**Notification:** `⚠️ WARNING`

---

## 🔐 Détection et Blocage SSH

### Détection SSH

Le système détecte une tentative SSH quand :
- Port = **22**
- Requête contient **"ssh"** (case-insensitive)
- Requête contient **"SSH"**
- Requête contient **"OpenSSH"**

### Actions Automatiques

```python
if SSH_attempt and IS_UNKNOWN:
    # 1. Bloquer immédiatement
    block_ip(ip)
    
    # 2. Ping la machine
    ping_and_shutdown(ip)
    
    # 3. Éteindre la machine
    subprocess.run(["ssh", f"root@{ip}", "shutdown -h now"])
    
    # 4. Enregistrer (blocked_ips.conf)
    # 5. Notification BLOCKED
```

---

## ⏱️ Chronologie : Machine Inconnue qui Tente SSH

| Temps | Événement | Action | Notification |
|-------|-----------|--------|--------------|
| T=0s | Machine inconnue se connecte | Tracking actif | ⚠️ WARNING |
| T=1s | Connexion acceptée (temporaire) | - | - |
| T=5s | Tente SSH (port 22) | **DÉTECTION SSH** | - |
| T=5s | `ping 192.168.43.165` | ✓ Réponse | - |
| T=5s | `ssh root@192.168.43.165 "shutdown -h now"` | Envoi commande | - |
| T=5s | Machine expulsée du réseau | iptables DROP | 🚫 BLOCKED |
| T=5s | IP bloquée définitivement | blocked_ips.conf | 🚫 BLOCKED |

---

## 🛡️ Implémentation Détaillée

### Fonction : `ping_and_shutdown(ip)`

```python
def ping_and_shutdown(ip):
    """
    Ping une machine et l'éteint avec 'shutdown -h now'
    Utilisé pour les machines inconnues qui tentent SSH
    """
    # Vérifier la machine est accessible
    ping_result = subprocess.run(["ping", "-c", "1", "-W", "2", ip])
    
    if ping_result.returncode == 0:
        # Machine accessible
        # Envoyer: ssh root@IP "shutdown -h now"
        subprocess.run(["ssh", "-o", "ConnectTimeout=2",
                       f"root@{ip}", "shutdown -h now"])
```

### Intégration dans `check_and_handle_unknown()`

```python
if is_ssh_attempt and not is_authorized:
    # Machine inconnue tente SSH
    log_to_file("SSH INCONNUE BLOQUÉE - PING + SHUTDOWN", "ERROR")
    
    # Ping + Shutdown
    ping_and_shutdown(ip)  # 🔴 ACTION!
    
    # Bloquer avec iptables
    block_ip(ip)
    
    return ("BLOCKED", 0)
```

---

## 📊 États et Transitions

```
┌─────────────────────────────────────────────────────────────┐
│                    MACHINE INCONNUE                         │
│                    (IP 150-200)                             │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   [ACTIF]              [INACTIF 15s]
        │                     │
        ├─ Requête normale    │
        │  → Acceptée         │
        │                     │
        └─ SSH DÉTECTÉ        │
           → PING + SHUTDOWN  │
           → BLOCAGE          │
                              │
                    ┌─────────┴─────────┐
                    │                   │
              [EXPULSION]          [BLOQUÉE]
                    │                   │
            iptables DROP       iptables DROP
            notifications.log   blocked_ips.conf
```

---

## 🚨 Fichiers Affectés

| Fichier | Description | Modification |
|---------|-------------|-------------|
| `tcp_server_simple.py` | Serveur principal | ✅ Ajout `ping_and_shutdown()`, SSH detection |
| `notifications.log` | Log des alertes | Nouvelles entrées BLOCKED |
| `blocked_ips.conf` | IPs bloquées | Machine ajouter après SSH |
| `Connexion.log` | Log détaillé | Enregistrement SSH attempt |

---

## 📝 Exemple de Log Complet

### Fichier: `notifications.log`

```
[2025-01-28 14:23:45] [WARNING] ⚠️ MACHINE INCONNUE DÉTECTÉE: 192.168.43.165:5050
[2025-01-28 14:23:47] [BLOCKED] 🚫 TENTATIVE SSH MACHINE INCONNUE: 192.168.43.165 - BLOQUÉE & EXPULSÉE!
[2025-01-28 14:23:47] [CRITICAL] 🔴 PING OK 192.168.43.165 - Envoi shutdown -h now
[2025-01-28 14:23:48] [CRITICAL] ✓ Shutdown SSH envoyé à 192.168.43.165
```

### Fichier: `Connexion.log`

```
[2025-01-28 14:23:45] [WARNING] ⚠️ MACHINE INCONNUE DÉTECTÉE: 192.168.43.165:5050 (15s avant expulsion)
[2025-01-28 14:23:47] [ERROR] 🚫 TENTATIVE SSH MACHINE INCONNUE BLOQUÉE: 192.168.43.165:5050 - EXPULSÉE!
[2025-01-28 14:23:47] [CRITICAL] 🔴 PING OK 192.168.43.165 - Envoi shutdown -h now
```

### Fichier: `blocked_ips.conf`

```
# IPs bloquées de manière permanente
192.168.43.165
```

---

## 🔧 Configuration

### Timeout d'Inactivité

```python
TIMEOUT_UNKNOWN = 15  # 15 secondes
```

**Localisation:** `tcp_server_simple.py` ligne 20

### Plage IP Dynamique

```python
# Machines avec IP 150-200 = INCONNUES
# Machines avec IP 100-149 = AUTORISÉES (devices.conf)
```

---

## ✅ Checklist de Vérification

- [x] Détection des connexions inconnues (IP dynamique)
- [x] Tracking 15 secondes d'inactivité
- [x] Expulsion automatique après timeout
- [x] Détection SSH (port 22, "ssh", "SSH", "OpenSSH")
- [x] Blocage SSH pour inconnues
- [x] Fonction `ping_and_shutdown()`
- [x] Intégration SSH detection dans le flow
- [x] Notifications WARNING/BLOCKED
- [x] iptables DROP automatique
- [x] Ajout à blocked_ips.conf
- [x] Threading monitoring pour timeout
- [x] Logging complet

---

## 🧪 Comment Tester

```bash
# 1. Lancer le serveur
python3 backend/serveur/tcp_server_simple.py

# 2. Simuler connexion inconnue
echo "test" | nc 192.168.43.150 5050

# 3. Observer les notifications
tail -f logs/notifications.log

# 4. Tenter SSH (doit déclencher ping + shutdown)
ssh root@192.168.43.150

# 5. Vérifier blocage
grep "192.168.43.150" backend/config/blocked_ips.conf
```

---

## 🎯 Résumé

| Scénario | Résultat |
|----------|----------|
| **Machine autorisée** → Connexion | ✅ Acceptée (SSH OK) |
| **Machine inconnue** → Idle 15s | ❌ Expulsion automatique |
| **Machine inconnue** → SSH | 🔴 **PING + SHUTDOWN** + Blocage |
| **Machine bloquée** → Connexion | ❌ Refusée (iptables DROP) |

---

## ⚡ Performance & Sécurité

- **Monitoring:** Thread séparé (ne bloque pas le serveur)
- **Ping timeout:** 2 secondes (rapide)
- **SSH timeout:** 2 secondes (rapide)
- **Pas de faux positifs:** Validation MAC + IP
- **Protection complète:** iptables + fichier config

