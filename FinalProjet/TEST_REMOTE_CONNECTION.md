# 🔌 Tester la Connexion Serveur depuis Une Autre Machine

## 📊 Configuration Serveur

- **Port**: 5050
- **Hôte**: 0.0.0.0 (écoute sur toutes les interfaces)
- **Protocole**: TCP Socket
- **Format**: Texte plain

---

## 🖥️ Étapes de Configuration

### 1. Démarrer le Serveur (Machine 1 - Serveur)

```bash
# Terminal 1 - Serveur
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet
python3 backend/serveur/log_server.py
```

**Résultat attendu**:
```
✓ Serveur de logs démarré sur 0.0.0.0:5050
✓ Fichier de log: ./logs/Connexion.log
✓ En attente de connexions...
```

### 2. Obtenir l'IP du Serveur

**Sur le serveur**:
```bash
# Méthode 1: IP locale (réseau)
hostname -I
# Résultat: 192.168.1.XX

# Méthode 2: Voir l'interface active
ip addr show
# ou
ifconfig
```

**Exemple**: Supposons que le serveur a l'IP `192.168.1.100`

---

## 🧪 Tests Disponibles

### **Option 1: Utiliser le script socket_client.sh (Plus simple)**

#### Sur la machine cliente (Machine 2):

```bash
# Syntaxe:
bash /path/to/socket_client.sh <SERVER_IP> <PORT> <MODE> [LIMIT]

# Exemples:
bash socket_client.sh 192.168.1.100 5050 realtime 5
bash socket_client.sh 192.168.1.100 5050 history 10
bash socket_client.sh 192.168.1.100 5050 stream
```

**Modes disponibles**:
- `realtime` - Derniers logs en temps réel
- `history` - Historique complet des logs
- `stream` - Flux continu de logs

**Exemple complet**:
```bash
# Machine Cliente
bash socket_client.sh 192.168.1.100 5050 realtime 5

# Résultat:
# [2026-01-20 10:15:32] INFO: Connection from 192.168.1.150
# [2026-01-20 10:15:33] SUCCESS: Device registered
# ...
```

---

### **Option 2: Utiliser netcat (nc)**

#### Test rapide de connexion:

```bash
# Machine Cliente - Test si le port est ouvert
nc -zv 192.168.1.100 5050

# Résultat si ok:
# Connection to 192.168.1.100 5050 port [tcp/*] succeeded!

# Résultat si erreur:
# nc: connect to 192.168.1.100 port 5050 (tcp) failed: Connection refused
```

#### Recevoir les logs via netcat:

```bash
# Machine Cliente - Se connecter et lire les logs
nc 192.168.1.100 5050 < <(echo "realtime 5")

# Ou pour rester connecté:
(echo "realtime 5"; sleep 2) | nc 192.168.1.100 5050
```

---

### **Option 3: Utiliser socat**

```bash
# Machine Cliente
socat - TCP:192.168.1.100:5050

# Puis taper dans le terminal interactif:
# realtime 5
# [ENTER]
```

---

### **Option 4: Utiliser bash TCP (natif, pas de dépendances)**

```bash
# Machine Cliente
exec 3<>/dev/tcp/192.168.1.100/5050
echo "realtime 5" >&3
cat <&3
exec 3>&-
```

---

### **Option 5: Test depuis Python**

```bash
# Machine Cliente
python3 << 'EOF'
import socket
import sys

try:
    # Connexion
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("192.168.1.100", 5050))
    print("✓ Connecté au serveur!")
    
    # Envoyer commande
    sock.send(b"realtime 5\n")
    
    # Recevoir réponse
    response = sock.recv(4096).decode()
    print("\n📋 Réponse du serveur:\n")
    print(response)
    
    sock.close()
    
except Exception as e:
    print(f"✗ Erreur: {e}")
EOF
```

---

## 📍 Configurations Réseau Possibles

### Scénario 1: Réseau Local (Recommandé pour tests)

```
Machine Serveur: 192.168.1.100
Machine Cliente: 192.168.1.150
Port: 5050
```

**Test depuis la machine cliente**:
```bash
bash socket_client.sh 192.168.1.100 5050 realtime 5
```

### Scénario 2: Même machine (localhost)

```
Serveur: localhost ou 127.0.0.1:5050
Client: localhost ou 127.0.0.1:5050
```

**Test depuis la même machine**:
```bash
# Terminal 1: Serveur
python3 backend/serveur/log_server.py

# Terminal 2: Cliente
bash socket_client.sh 127.0.0.1 5050 realtime 5
```

### Scénario 3: Réseau distant

```
Machine Serveur: IP_PUBLIQUE:5050
Machine Cliente: Anywhere
```

⚠️ **Attention**: Nécessite de configurer le firewall/port forwarding

---

## 🔍 Commandes de Diagnostic

### Vérifier que le serveur écoute:

**Sur le serveur**:
```bash
# Vérifier les ports ouverts
lsof -i :5050
netstat -tlnp | grep 5050
ss -tlnp | grep 5050

# Résultat attendu:
# LISTEN 0.0.0.0:5050
```

### Tester la connectivité réseau:

**Depuis la cliente vers le serveur**:
```bash
# Vérifier la route réseau
ping 192.168.1.100

# Vérifier le port spécifique
nc -zv 192.168.1.100 5050
telnet 192.168.1.100 5050  # Puis Ctrl+] quit
```

### Voir les connexions en cours:

**Sur le serveur**:
```bash
# Connexions établies
netstat -tnp | grep ESTABLISHED
ss -tnp | grep ESTABLISHED

# Avec plus de détails
watch -n1 'netstat -tnp | grep 5050'
```

---

## 📋 Checklist de Test

- [ ] Serveur démarre sans erreur: `python3 backend/serveur/log_server.py`
- [ ] Port 5050 écoute: `lsof -i :5050`
- [ ] Firewall permet le trafic: `sudo ufw allow 5050`
- [ ] Ping vers le serveur: `ping 192.168.1.100`
- [ ] Port accessible: `nc -zv 192.168.1.100 5050`
- [ ] Réception de logs: `bash socket_client.sh 192.168.1.100 5050 realtime 5`

---

## 🐛 Troubleshooting

### Erreur: "Connection refused"

```bash
# Solution: Vérifier que le serveur tourne
lsof -i :5050

# Si pas de résultat, relancer le serveur
cd /FinalProjet && python3 backend/serveur/log_server.py
```

### Erreur: "No route to host"

```bash
# Solution: Vérifier connectivité réseau
ping 192.168.1.100
route -n
traceroute 192.168.1.100
```

### Erreur: "Permission denied" (port < 1024)

```bash
# Solution: Utiliser un port > 1024 (déjà le cas, 5050 OK)
# Ou lancer avec sudo si nécessaire
sudo python3 backend/serveur/log_server.py
```

### Script socket_client.sh: "command not found"

```bash
# Solution: Utiliser le chemin complet
bash /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/scripts/socket_client.sh 192.168.1.100 5050 realtime 5

# Ou le rendre exécutable
chmod +x socket_client.sh
./socket_client.sh 192.168.1.100 5050 realtime 5
```

---

## 📝 Exemple Complet de Test

### Machine 1 (Serveur 192.168.1.100)

```bash
# Terminal 1: Lancer le serveur
cd /FinalProjet
python3 backend/serveur/log_server.py

# [Résultat attendu]
# ✓ Serveur de logs démarré sur 0.0.0.0:5050
# ✓ En attente de connexions...
```

### Machine 2 (Cliente 192.168.1.150)

```bash
# Terminal 1: Vérifier la connexion
nc -zv 192.168.1.100 5050
# Résultat: Connection to 192.168.1.100 5050 port [tcp/*] succeeded!

# Terminal 2: Récupérer les logs
bash socket_client.sh 192.168.1.100 5050 realtime 5

# [Résultat attendu]
# [2026-01-20 10:15:32] Connection from 192.168.1.150
# [2026-01-20 10:15:33] Device 192.168.1.150 (AA:BB:CC:DD:EE:FF) logged in
# ...
```

### Machine 1 (Serveur) - Observer les connexions

```bash
# Terminal 2: Voir les connexions entrantes
watch -n1 'netstat -tnp | grep 5050'

# [Résultat]
# tcp    0    0 0.0.0.0:5050    0.0.0.0:*    LISTEN    12345/python3
# tcp    0    0 192.168.1.100:5050    192.168.1.150:XXXXX    ESTABLISHED    12345/python3
```

---

## ⚡ Commandes Rapides

```bash
# Copier-coller prêt à l'emploi

# Test 1: Ping
ping 192.168.1.100

# Test 2: Port ouvert?
nc -zv 192.168.1.100 5050

# Test 3: Lire les logs
bash socket_client.sh 192.168.1.100 5050 realtime 5

# Test 4: Voir les connexions serveur
lsof -i :5050

# Test 5: Logs persistants
bash socket_client.sh 192.168.1.100 5050 history 20
```

---

**État**: Prêt pour test multi-machine ✅
**Date**: 20 janvier 2026
