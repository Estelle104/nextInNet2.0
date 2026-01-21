# 📡 Comment Lancer le Réseau WiFi

## 🚀 Procédure Complète (3 étapes)

### **Étape 1️⃣ : Configuration (une seule fois)**

```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet

# Configurer l'interface et le réseau
./configure_ap.sh
```

**Vous serez demandé:**
- Interface réseau: **`wlo1`**
- Confirmation: **`o`**

**Résultat attendu:**
```
✓ Interface: wlo1
✓ Point d'accès configuré
```

---

### **Étape 2️⃣ : Lancer le Point d'Accès WiFi (Terminal 1)**

```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet

# Lancer le WiFi (doit rester ouvert)
sudo ./launch_ap.sh wlo1
```

**Résultat attendu:**
```
📡 Point d'Accès WiFi - Informations
  SSID: NextInNet-Secure
  Mot de passe: SecureNetwork123
  Interface: wlo1
  IP Gateway: 192.168.43.1
  Pool DHCP: 192.168.43.100-200

🚀 Lancement de hostapd...
```

**À partir de là, les autres machines verront le réseau "NextInNet-Secure" !**

---

### **Étape 3️⃣ : Lancer le Système (Terminal 2, dans un autre terminal)**

```bash
cd /home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet

# Démarrer le serveur DHCP + TCP
./start_system.sh
```

**Sélectionner l'option:** `1` (Tous les services)

---

## ✅ Vérification

Après ces 3 étapes, vous devriez voir:

| Élément | Où le voir | Signe de succès |
|---------|-----------|-----------------|
| **Point d'accès WiFi visible** | Sur le téléphone/autre PC | Voir "NextInNet-Secure" |
| **Serveur DHCP actif** | Terminal 1 (launch_ap.sh) | Le terminal reste actif |
| **Système démarré** | Terminal 2 (start_system.sh) | Menu du système visible |

---

## 📱 Connexion depuis une Autre Machine

1. **Sur votre téléphone ou autre PC:**
   - Chercher le réseau: **`NextInNet-Secure`**
   - Mot de passe: **`SecureNetwork123`**
   - Vous devriez recevoir une IP: **`192.168.43.1xx`**

2. **Vérifier les logs:**
   ```bash
   # Ouvrir un 3e terminal
   tail -f backend/logs/dhcp.log
   ```
   
   Vous verrez:
   ```
   [2026-01-20 10:31:02] ✓ IP assignée: AA:BB:CC:DD:EE:FF -> 192.168.43.100
   ```

---

## 🛑 Pour Arrêter

- **Point d'accès:** `Ctrl+C` dans Terminal 1
- **Système:** `Ctrl+C` dans Terminal 2
- **Tout nettoyer:**
  ```bash
  sudo systemctl start NetworkManager
  ```

---

## 🔧 Configuration WiFi

Si vous voulez changer le nom ou le mot de passe du WiFi:

Éditer `/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/launch_ap.sh`

Lignes à modifier:
```bash
ssid=NextInNet-Secure           # ← Nom du réseau
wpa_passphrase=SecureNetwork123  # ← Mot de passe
```

---

## � Ajouter des Machines Autorisées

Pour qu'une machine externe puisse se connecter:

1. **Vérifier sa MAC dans les logs DHCP:**
   ```bash
   tail -f backend/logs/dhcp.log
   # Vous verrez: "✗ MAC non autorisée: 4E:E0:B8:0F:09:78"
   ```

2. **Ajouter la MAC dans `backend/config/devices.conf`:**
   ```bash
   nano backend/config/devices.conf
   ```
   
   Ajouter une ligne:
   ```
   4E:E0:B8:0F:09:78|192.168.43.110|Nom_De_La_Machine
   ```

3. **Redémarrer le serveur DHCP** pour charger la nouvelle configuration

Maintenant la machine recevra une IP DHCP et pourra se connecter ! ✅
