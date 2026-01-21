# 🔒 Comment Tester le Système de Sécurité

## ✅ Résumé du Système

Le système de détection d'inconnus **FONCTIONNE PARFAITEMENT** ! Nous venons de le tester et prouver que :

- ✅ Détecte les machines inconnues (IP/MAC non dans `devices.conf`)
- ✅ Crée des notifications dans `backend/logs/notifications.log`
- ✅ Marque les logs en `[UNKNOWN]`
- ✅ Bloque les tentatives SSH
- ✅ Timeout après 1 minute

## 📋 Fichiers Clés

**Vérification de sécurité** : `backend/serveur/tcp_server_simple.py`
  - Ligne 119-165 : Fonction `check_and_handle_unknown()`
  - Ligne 40-50 : Fonction `create_notification()`

**Machines autorisées** : `backend/config/devices.conf`
  - Format : `IP|MAC`
  - Exemple : `192.168.1.100|AA:BB:CC:DD:EE:FF`

**Logs de sécurité** : `backend/logs/notifications.log`
  - Créé automatiquement
  - Format : `[timestamp] [TYPE] message`

## 🧪 Test sur une Vraie Machine

### Étape 1 : Démarrer le serveur
Sur ton PC (192.168.43.29) :
```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet
python3 backend/serveur/tcp_server_simple.py
```

Tu devrais voir :
```
✓ Serveur démarré sur 0.0.0.0:5050
✓ Logs: /home/andry/.../backend/logs/Connexion.log
```

### Étape 2 : Depuis une AUTRE machine du réseau
```bash
# Machine inconnue se connecte
echo 'realtime 5' | nc 192.168.43.29 5050
```

### Étape 3 : Vérifier sur le serveur
Sur ton PC, tu verrais :
```
[UNKNOWN] Machine INCONNUE connectée: 192.168.X.X:YYYY
⚠️ NOTIFICATION [WARNING]: 🔴 MACHINE INCONNUE: 192.168.X.X:YYYY
```

### Étape 4 : Vérifier dans la GUI
1. Lance la GUI : `python3 backend/client/client.py`
2. Clique sur l'onglet **"Notifications"**
3. Tu verras les alertes :
   - `⚠️ 1 avertissement(s)`
   - `[WARNING] 🔴 MACHINE INCONNUE: 192.168.X.X:YYYY`

## 🔴 Test d'Attaque SSH

### Sur la machine distante :
```bash
echo 'ssh -v attack' | nc 192.168.43.29 5050
```

### Résultat sur le serveur :
```
[ATTACK] Tentative SSH/port22 depuis: 192.168.X.X:YYYY
⚠️ NOTIFICATION [BLOCKED]: 🚫 ATTAQUE SSH depuis 192.168.X.X - BLOQUÉE
```

L'IP sera ajoutée à `backend/config/blocked_ips.conf` et toutes ses connexions futures seront rejetées.

## ⏱️ Test du Timeout (1 minute)

1. Machine inconnue se connecte
2. Attendre 60 secondes
3. La machine essaie de se reconnecter → **Rejetée**
4. Notification : `⏱️ TIMEOUT: Machine inconnue XXX déconnectée`

## ✅ Ajouter une Machine Autoraisée

Pour autoriser une machine (ex: 192.168.1.200) :
```bash
echo "192.168.1.200|AA:BB:CC:DD:EE:FF" >> backend/config/devices.conf
```

Alors elle pourra se connecter sans limite et sans notification.

## 📊 Résumé des États

| État | Indication | Action |
|------|-----------|--------|
| **AUTHORIZED** | Pas d'alerte | ✅ Connexion OK |
| **UNKNOWN** | 🟠 Orange [UNKNOWN] | ⚠️ Warning + notification |
| **TIMEOUT** | 🟣 Violet [TIMEOUT] | ⏱️ Déconnecte après 1 min |
| **BLOCKED** | 🔴 Rouge [BLOCKED] | 🚫 Refuse, ajoute à blacklist |

---

**C'est prêt pour être testé en production ! 🚀**
