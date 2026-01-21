# 📋 Architecture du Projet - FinalProjet

## Vue d'ensemble

**FinalProjet** est un système de gestion de réseau WiFi avec interface de contrôle. Il fournit :
- 🔌 **Serveur DHCP** pour l'allocation d'adresses IP
- 📊 **Serveur TCP** pour la gestion des logs et connexions
- 🎨 **Interface GUI** (tkinter) pour l'administration
- 🔒 **Gestion des utilisateurs et appareils**
- 📢 **Système de notifications** en temps réel

---

## 📁 Structure complète

```
FinalProjet/
├── 📄 Fichiers de configuration et démarrage
├── backend/               # Logique serveur (Python)
├── frontend/              # Interface graphique (tkinter)
├── logs/                  # Fichiers de journalisation
└── demmarer/             # Scripts de démarrage du système
```

---

## 📄 Fichiers racine

### `configure_ap.sh`
- **Rôle**: Script de configuration du point d'accès WiFi
- **Fonction**: Configure hostapd, dnsmasq, interfaces réseau
- **Utilisé pour**: Initialisation du système WiFi lors du démarrage

### `start_system.sh`
- **Rôle**: Script de démarrage principal du système
- **Fonction**: Lance tous les services (DHCP, TCP server, frontend GUI)
- **Utilisé pour**: Lancer le projet complet

### `SYSTEM_STATUS.txt`
- **Rôle**: Fichier de statut du système
- **Fonction**: Enregistre l'état actuel des services
- **Contenu**: Statuts des serveurs, interfaces, configurations

### `TEST_INSTRUCTIONS.md`
- **Rôle**: Documentation des tests
- **Fonction**: Guide d'exécution des tests unitaires et d'intégration
- **Contenu**: Commandes de test pour chaque composant

### `README_TESTS.md`
- **Rôle**: Rapport détaillé des tests
- **Fonction**: Résultats et procédures de test complètes

---

## 🔧 Dossier: `backend/`
**Cœur du système** - Tous les services serveur

### 📁 `backend/serveur/` - Serveurs TCP/DHCP

#### `dhcp_server.py` ⭐
- **Rôle**: Serveur DHCP principal
- **Port**: 67/UDP  (ecoute)
- **Fonction**:
  - Alloue les adresses IP aux appareils
  - Valide l'autorisation (MAC|IP dans `devices.conf`)
  - Envoie des notifications pour appareils inconnus
  - Gère les leases (durée 3600s)
- **Détection**: 
  - ✓ Appareils autorisés → IP attribuée + notification INFO
  - ⚠️ Appareils inconnues → Pas d'IP + notification WARNING
- **Dépendances**: `config/devices.conf`, `logs/notifications.log`

#### `tcp_server_simple.py` ⭐
- **Rôle**: Serveur TCP pour les logs et connexions
- **Port**: 5050/TCP
- **Fonction**:
  - Écoute les connexions des appareils
  - Enregistre les connexions dans `logs/Connexion.log`
  - Bloque les IPs suspectes
  - Envoie les logs demandés aux clients
- **Format log**: `[HH:MM:SS] [TYPE] Message`
- **Dépendances**: `config/blocked_ips.conf`, `logs/Connexion.log`

### 📁 `backend/config/` - Fichiers de configuration

#### `server.conf`
- **Rôle**: Configuration générale du serveur
- **Contenu**:
  - `LOG_PORT=5050` - Port du serveur TCP
  - `DHCP_INTERFACE=wlo1` - Interface WiFi
  - `LOG_FILE_PATH=logs/Connexion.log` - Chemin des logs

#### `users.conf`
- **Rôle**: Base de données des utilisateurs
- **Format**: `username:password_hashed`
- **Exemple**:
  ```
  admin:hashed_password_123
  user1:hashed_password_456
  ```
- **Utilisé par**: Interface d'authentification, gestion des comptes

#### `devices.conf` ⭐
- **Rôle**: Liste des appareils autorisés
- **Format**: `MAC_ADDRESS|IP_ADDRESS`
- **Exemple**:
  ```
  AA:BB:CC:DD:EE:FF|192.168.43.100
  D0:C5:D3:8C:09:1D|192.168.43.200
  1C:BF:CE:F1:F1:12|192.168.43.111
  ```
- **Validation**: DHCP accepte seulement les appareils listés ici

#### `blocked_ips.conf`
- **Rôle**: Liste des IPs bloquées
- **Format**: Une IP par ligne
- **Utilisé par**: TCP server pour refuser les connexions

#### `dhcp_leases.conf`
- **Rôle**: Base de données des locations DHCP actives
- **Format**: `MAC|IP|expiration_timestamp`
- **Utilisé par**: DHCP server pour gérer les leases

#### `logging.conf`
- **Rôle**: Configuration du logging Python
- **Contenu**: Règles de verbosité, formats de messages

#### `README_CONFIG.md`
- **Rôle**: Documentation des configurations
- **Contenu**: Explications détaillées de chaque paramètre

### 📁 `backend/data/` - Gestion des données

#### `users_data.py`
- **Rôle**: Module de gestion des utilisateurs
- **Fonction**:
  - Lecture/écriture dans `users.conf`
  - Hachage des mots de passe
  - Validation des identifiants
  - Vérification d'authentification

### 📁 `backend/logs/` - Fichiers de journalisation

#### `Connexion.log`
- **Rôle**: Journal principal des connexions
- **Format**: `[TIMESTAMP] [TYPE] [MESSAGE]`
- **Types**: `[SOCKET]` pour connexions TCP, `[TEST]` pour tests
- **Taille**: Accumule toutes les connexions du système

#### `notifications.log`
- **Rôle**: Alertes de sécurité
- **Types**:
  - `[INFO]` - Appareils autorisés acceptés
  - `[WARNING]` - Appareils inconnus détectés
  - `[BLOCKED]` - IPs bloquées
- **Utilisé par**: Interface notifications (affichage temps réel)

### 📁 `backend/scripts/` - Scripts utilitaires

#### `get_mac_address.py`
- **Rôle**: Utilitaire pour récupérer les MAC des interfaces
- **Utilisé pour**: Debug, obtenir MAC de la machine

#### `test_config.sh`
- **Rôle**: Tests des fichiers de configuration
- **Vérifie**: Existence et validité des fichiers config
- **Exécution**: `bash test_config.sh`

#### `test_socket_communication.sh`
- **Rôle**: Tests de communication socket
- **Vérifie**: Connexion TCP au port 5050
- **Exécution**: `bash test_socket_communication.sh`

#### `socket_client.sh`
- **Rôle**: Client socket en bash pour tester connexions
- **Usage**: `./socket_client.sh <host> <port> <command> [args]`
- **Commandes**: `realtime`, `history`, etc.

---

## 🎨 Dossier: `frontend/`
**Interface utilisateur** - Application tkinter GUI

### 📁 `frontend/views/` - Écrans de l'application

#### `main.py` ⭐
- **Rôle**: Point d'entrée de l'application
- **Fonction**:
  - Initialise la fenêtre tkinter
  - Lance tous les threads
  - Démarre le serveur DHCP et TCP
  - Affiche les notifications
- **Contenu**: Classe `MainWindow` avec navigation

#### `main_view.py`
- **Rôle**: Écran d'accueil principal
- **Contenu**:
  - Navigation vers autres sections
  - Statut du système
  - Badge de notifications

#### `create_user_view.py`
- **Rôle**: Création de nouveaux utilisateurs
- **Fonction**:
  - Formulaire d'inscription
  - Validation (pseudo ≥3 chars, mots de passe identiques)
  - Hachage et sauvegarde dans `users.conf`

#### `list_user_view.py`
- **Rôle**: Gestion des utilisateurs
- **Fonction**:
  - Affiche liste des utilisateurs
  - Suppression par double-clic
  - Confirmation de suppression

#### `logs_view.py`
- **Rôle**: Affichage des logs
- **Contenu**:
  - Lecture et affichage de `logs/Connexion.log`
  - Scrolling pour naviguer
  - Rafraîchissement automatique

#### `notifications_view.py` ⭐
- **Rôle**: Affichage des alertes de sécurité
- **Contenu**:
  - Lit `logs/notifications.log`
  - Filtre par type (INFO/WARNING/BLOCKED)
  - Code couleur:
    - 🔵 Bleu: INFO (appareils autorisés)
    - 🟠 Orange: WARNING (appareils inconnues)
    - 🔴 Rouge: BLOCKED (IPs bloquées)
  - Rafraîchissement chaque 2 secondes

### 📁 `frontend/views/users/` - Gestion appareils/utilisateurs

#### `create_user_view.py`
- **Rôle**: Enregistrement d'appareils (MAC|IP)
- **Fonction**:
  - Formulaire MAC et IP
  - Validation format MAC (XX:XX:XX:XX:XX:XX)
  - Validation IP (format et subnet 192.168.43.x)
  - Ajout dans `config/devices.conf`

#### `list_user_view.py`
- **Rôle**: Gestion des appareils autorisés
- **Fonction**:
  - Affiche liste des appareils (MAC|IP)
  - Suppression par sélection
  - Confirmation avant suppression

### 📁 `frontend/assets/` - Ressources

#### `theme.py`
- **Rôle**: Configuration des couleurs et styles
- **Contenu**:
  - Palettes de couleurs
  - Polices
  - Dimensions des widgets

---

## 📊 Dossier: `logs/`
**Stockage centralisé des logs**

- **Connexion.log** - Toutes les connexions TCP
- **notifications.log** - Alertes de sécurité
- Format unifié: `[TIMESTAMP] [TYPE] [MESSAGE]`

---

## 🚀 Dossier: `demmarer/`
**Scripts de démarrage**

- Contient les scripts pour initialiser et lancer le système complet

---

## 🔄 Flux d'exécution

### Démarrage du système
```
start_system.sh
    ↓
configure_ap.sh (configure WiFi)
    ↓
dhcp_server.py (port 67) - Lance serveur DHCP
    ↓
tcp_server_simple.py (port 5050) - Lance serveur TCP
    ↓
main.py - Lance interface GUI
    ↓
Système prêt ✓
```

### Connexion d'un appareil
```
Appareil se connecte → DHCP REQUEST (port 67)
    ↓
dhcp_server.py reçoit la requête
    ↓
Vérifie MAC dans devices.conf
    ↓
✓ Si autorisé:
  - Alloue IP
  - Notification INFO
  - Appareil reçoit IP
    
✗ Si inconnue:
  - Pas d'IP
  - Notification WARNING
  - Badge ⚠️ dans interface
```

### Reconnexion au TCP server
```
Appareil envoie log → TCP server (port 5050)
    ↓
tcp_server_simple.py reçoit connexion
    ↓
Enregistre dans Connexion.log
    ↓
Affiche dans interface logs_view
```

---

## 📡 Communication entre composants

```
┌─────────────────────────────────────────────────────┐
│                  FRONTEND (tkinter)                 │
│  main_view → logs_view → notifications_view → etc   │
└─────────────────┬───────────────────────────────────┘
                  │
        ┌─────────┼─────────┐
        ↓         ↓         ↓
   users.conf logs/ notifications/
        ↑         ↑         ↑
        └─────────┼─────────┘
                  │
┌─────────────────┴───────────────────────────────────┐
│                BACKEND (Python)                     │
│  ┌──────────────┐        ┌──────────────┐          │
│  │ DHCP Server  │        │ TCP Server   │          │
│  │ (port 67)    │        │ (port 5050)  │          │
│  └──────────────┘        └──────────────┘          │
└─────────────────────────────────────────────────────┘
        ↑                           ↑
        │                           │
   Appareils WiFi         Appareils (logs)
```

---

## 🔒 Fichiers de sécurité

| Fichier | Contenu | Accès |
|---------|---------|-------|
| `users.conf` | Comptes utilisateurs | ⚠️ Privé |
| `devices.conf` | Appareils autorisés | ⚠️ Privé |
| `blocked_ips.conf` | IPs bloquées | ⚠️ Privé |
| `dhcp_leases.conf` | Leases actives | ⚠️ Privé |
| `notifications.log` | Alertes sécurité | ⚠️ Privé |

---

## 🎯 Points clés du système

✓ **DHCP Server** - Contrôle l'accès au WiFi via whitelist MAC|IP  
✓ **TCP Server** - Enregistre toutes les connexions pour audit  
✓ **Notifications** - Alertes en temps réel sur appareils inconnues  
✓ **GUI** - Interface simple pour administration  
✓ **Logs centralisés** - Traçabilité complète  

---

## 📝 Configuration rapide

### Ajouter un appareil autorisé:
1. Interface → Créer utilisateur (device)
2. Entrer MAC (format: XX:XX:XX:XX:XX:XX)
3. Entrer IP (format: 192.168.43.X)
4. Valider → Ajout dans `devices.conf`

### Voir les connexions:
1. Interface → Logs
2. Consulter `Connexion.log` en temps réel

### Voir alertes de sécurité:
1. Interface → Notifications
2. Badge 🔔 affiche nombre d'alertes
3. Consultez les appareils inconnues détectées

---

**Version**: 1.0  
**Date**: 21 janvier 2026  
**Statut**: Système complet et opérationnel
