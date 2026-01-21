# 🚀 Test Connexion Serveur - Guide Rapide

## ⚡ En 3 Étapes

### Étape 1: Démarrer le Serveur

**Sur la machine serveur (ex: 192.168.1.100)**:
```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet
python3 backend/serveur/log_server.py
```

### Étape 2: Trouver l'IP du Serveur

```bash
# Sur le serveur, exécuter:
hostname -I
# ou
ip addr | grep "inet " | grep -v 127.0.0.1
```

**Résultat exemple**: `192.168.1.100`

### Étape 3: Tester depuis la Machine Cliente

**Sur n'importe quelle autre machine**:

```bash
# Option A: Simple avec netcat (teste la connexion)
nc -zv 192.168.1.100 5050

# Option B: Récupérer les logs avec bash
bash /path/to/socket_client.sh 192.168.1.100 5050 realtime 5

# Option C: Python
python3 << 'EOF'
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("192.168.1.100", 5050))
sock.send(b"realtime 5\n")
print(sock.recv(4096).decode())
sock.close()
EOF
```

---

## 📋 Commandes Copiables

### Vérifier la connectivité

```bash
# Machine cliente
ping 192.168.1.100
```

### Tester le port

```bash
# Machine cliente
nc -zv 192.168.1.100 5050
# Résultat si OK: "Connection...succeeded!"
```

### Voir les logs du serveur

```bash
# Machine cliente
bash socket_client.sh 192.168.1.100 5050 realtime 5
```

### Voir l'historique complet

```bash
# Machine cliente  
bash socket_client.sh 192.168.1.100 5050 history 20
```

---

## 🐛 Si ça ne marche pas

```bash
# 1. Vérifier que le serveur tourne
ps aux | grep log_server

# 2. Vérifier que le port est ouvert
lsof -i :5050

# 3. Vérifier le firewall
sudo ufw status
sudo ufw allow 5050

# 4. Voir les erreurs serveur
journalctl -u your-service (si service)
# ou regarder la sortie du terminal où c'est lancé
```

---

## 📍 Remplacer l'IP

Dans tous les exemples, remplacer `192.168.1.100` par:
- L'IP de votre serveur (voir `hostname -I` sur le serveur)
- Ou `127.0.0.1` si vous testez sur la même machine
- Ou `localhost` si vous testez sur la même machine

---

## ✅ Cas Nominal

```
Machine A (192.168.1.100)          Machine B (192.168.1.150)
├─ Terminal 1:                     ├─ Terminal 1:
│  $ python3 log_server.py        │  $ ping 192.168.1.100
│  ✓ Port 5050 listen             │  ✓ Connected
│  ✓ Waiting...                   │
│                                  ├─ Terminal 2:
│                                  │  $ nc -zv 192.168.1.100 5050
│                                  │  ✓ Succeeded
│                                  │
│                                  ├─ Terminal 3:
│                                  │  $ bash socket_client.sh 192.168.1.100 5050 realtime 5
│  ✓ Client connected              │  ✓ [logs reçus]
│  ✓ Sending logs...              │
```

---

**État**: Prêt à l'emploi ✅
