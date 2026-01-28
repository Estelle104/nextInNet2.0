# 🏗️ Architecture & Flux d'Exécution - NextInNet

## 📊 Vue d'ensemble globale

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SYSTÈME NEXTINNET 2.0                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  🖥️  POINT D'ACCÈS WIFI (PC Serveur)                               │
│  ├─ Interface WiFi: wlo1                                            │
│  ├─ IP: 192.168.43.1                                               │
│  └─ SSID: NextInNet                                                 │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ SERVICES BACKEND (Python)                                   │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │ 1. SERVEUR DHCP (Port 67/UDP)                               │   │
│  │    └─ Alloue adresses IP aux appareils                      │   │
│  │                                                              │   │
│  │ 2. SERVEUR TCP (Port 5050/TCP)                              │   │
│  │    └─ Gère logs & connexions                                │   │
│  │                                                              │   │
│  │ 3. CONFIGURATIONS                                            │   │
│  │    ├─ devices.conf (MAC|IP autorisés)                       │   │
│  │    ├─ users.conf (authentification)                         │   │
│  │    ├─ blocked_ips.conf (IPs bloquées)                       │   │
│  │    └─ server.conf (paramètres généraux)                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ INTERFACE FRONTEND (Tkinter GUI)                            │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │ • Gestion des utilisateurs (créer/lister)                  │   │
│  │ • Gestion des appareils                                     │   │
│  │ • Visualisation des logs                                    │   │
│  │ • Notifications en temps réel                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
         ⬇️
┌─────────────────────────────────────────────────────────────────────┐
│  📱 APPAREILS CLIENTS (Smartphones, Laptops, etc)                   │
│  ├─ Se connectent au WiFi "NextInNet"                              │
│  ├─ Reçoivent adresse IP via DHCP                                  │
│  └─ Communiquent via TCP port 5050                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 ÉTAPES D'EXÉCUTION

### **ÉTAPE 1: Démarrage du système** ⏱️ (~30 secondes)

```bash
bash start_system.sh
```

**Séquence:**

```
┌─────────────────────────────────────────────────────┐
│ 1. Vérification configuration système               │
│    └─ Vérifie /etc/nextinnet.conf                   │
│    └─ Charge interfaces WiFi et WAN                 │
│                                                      │
│ 2. Arrêt services conflictuels                      │
│    └─ NetworkManager STOP                           │
│    └─ wpa_supplicant STOP                           │
│                                                      │
│ 3. Configuration réseau AP                          │
│    └─ Configure IP 192.168.43.1 sur wlo1            │
│    └─ Active forwarding & NAT (iptables)            │
│                                                      │
│ 4. Lancement services backend                       │
│    ├─ DHCP Server (Port 67/UDP)                     │
│    │  └─ Écoute les DHCP DISCOVER                   │
│    │  └─ Alloue IPs du pool 192.168.43.100-200      │
│    │                                                 │
│    └─ TCP Server (Port 5050/TCP)                    │
│       └─ Écoute les connexions clients               │
│       └─ Enregistre logs & connexions                │
│                                                      │
│ 5. Lancement interface GUI Frontend                 │
│    └─ Fenêtre Tkinter 900x650 pixels                │
│    └─ Affiche menu principal avec 4 onglets         │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

### **ÉTAPE 2: Connexion d'un appareil client** 📱

```
┌──────────────────────────────────────────────────────────────────┐
│ CLIENT (Smartphone / PC / Laptop)                                │
└──────────────────────────────────────────────────────────────────┘
                              ⬇️
        [Client scanne WiFi et voit "NextInNet"]
                              ⬇️
              [Client se connecte au réseau WiFi]
                              ⬇️
                    
    ┌────────────────────────────────────────────────────┐
    │ ÉTAPE 2.1: DISCOVERY DHCP (Client → Serveur)       │
    ├────────────────────────────────────────────────────┤
    │ 1. Client envoie DHCP DISCOVER (broadcast)         │
    │    └─ "Qui peut me donner une IP?"                 │
    │                                                     │
    │ 2. Serveur DHCP reçoit DISCOVER                    │
    │    └─ Lit MAC address du client                    │
    │    └─ Cherche MAC dans devices.conf                │
    │                                                     │
    │ 3. Serveur DHCP répond OFFER                       │
    │    ├─ SI MAC autorisé:                             │
    │    │  └─ Envoie IP assignée de devices.conf        │
    │    │  └─ Crée notification INFO                    │
    │    │                                                │
    │    └─ SI MAC inconnu:                              │
    │       └─ Envoie NACK (refus)                       │
    │       └─ Crée notification WARNING                 │
    │       └─ Ajoute IP à blocked_ips.conf              │
    │                                                     │
    └────────────────────────────────────────────────────┘
                              ⬇️
                    
    ┌────────────────────────────────────────────────────┐
    │ ÉTAPE 2.2: REQUEST DHCP (Si autorisé)              │
    ├────────────────────────────────────────────────────┤
    │ 1. Client envoie DHCP REQUEST                      │
    │    └─ "Je confirme vouloir cette IP"               │
    │                                                     │
    │ 2. Serveur DHCP répond ACK                         │
    │    └─ IP confirmée                                 │
    │    └─ Lease sauvegardé dans dhcp_leases.conf       │
    │       (expiration: dans 1 heure)                   │
    │                                                     │
    └────────────────────────────────────────────────────┘
                              ⬇️
                              
    ┌────────────────────────────────────────────────────┐
    │ ÉTAPE 2.3: CONNEXION TCP (Client → Serveur)        │
    ├────────────────────────────────────────────────────┤
    │ 1. Client établit connexion TCP port 5050          │
    │    └─ Envoie sa MAC & IP                           │
    │                                                     │
    │ 2. Serveur TCP reçoit connexion                    │
    │    ├─ Vérifie si IP est dans blocked_ips.conf      │
    │    │  ├─ SI bloquée: FERME connexion               │
    │    │  └─ LOG: "[HH:MM:SS] [BLOCKED] IP xxx"        │
    │    │                                                │
    │    └─ SI autorisée: ACCEPTE connexion              │
    │       ├─ Enregistre dans Connexion.log             │
    │       ├─ LOG: "[HH:MM:SS] [CONNECTED] MAC xxx"     │
    │       └─ Reste connecté jusqu'à déconnexion        │
    │                                                     │
    └────────────────────────────────────────────────────┘
                              ⬇️
             [Client obtient accès Internet]
```

---

### **ÉTAPE 3: Gestion via Interface GUI** 🖱️

```
┌─────────────────────────────────────────────────────────────┐
│ INTERFACE TKINTER - MENU PRINCIPAL                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ 1. 👥 CRÉER UTILISATEUR                                │
│  │    ├─ Entrée: username, password                        │
│  │    ├─ Action: Ajoute ligne à users.conf (hashed)       │
│  │    └─ Sauvegarde avec hash MD5/SHA256                   │
│  │                                                          │
│  ├─ 2. 📋 LISTER UTILISATEURS                              │
│  │    ├─ Lit users.conf                                    │
│  │    ├─ Affiche tableau: username | password_hash         │
│  │    └─ Permet édition/suppression                        │
│  │                                                          │
│  ├─ 3. 📊 VISUALISER LOGS                                  │
│  │    ├─ Onglet 1: Logs DHCP (dhcp.log)                   │
│  │    │  └─ "[HH:MM:SS] MAC xx -> IP yyyy"                 │
│  │    │                                                     │
│  │    ├─ Onglet 2: Logs Connexion (Connexion.log)         │
│  │    │  └─ "[HH:MM:SS] [CONNECTED] MAC xxx"              │
│  │    │  └─ "[HH:MM:SS] [BLOCKED] IP xxx"                 │
│  │    │                                                     │
│  │    └─ Onglet 3: Notifications (notifications.log)      │
│  │       └─ "[HH:MM:SS] [INFO] Appareil autorisé xxx"     │
│  │       └─ "[HH:MM:SS] [WARNING] Appareil inconnu xxx"   │
│  │                                                          │
│  └─ 4. 🔔 NOTIFICATIONS EN TEMPS RÉEL                      │
│       ├─ Affichage panneau notifications                   │
│       ├─ Auto-refresh toutes les 2 secondes                │
│       └─ Code couleur: ✓ INFO (vert), ⚠️ WARNING (jaune)   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### **ÉTAPE 4: Flux complet d'une connexion client** 🔄

```
CLIENT                          SERVEUR DHCP              SERVEUR TCP         GUI FRONTEND
   │                                 │                         │                    │
   │◄─── 1. Scan WiFi ──────────────►│                         │                    │
   │         "NextInNet"              │                         │                    │
   │                                  │                         │                    │
   │ 2. Se connecte au WiFi           │                         │                    │
   │    (authentification WiFi)       │                         │                    │
   │                                  │                         │                    │
   │◄──── 3. DHCP DISCOVER ──────────►│                         │                    │
   │      (Broadcast)                 │                         │                    │
   │                                  │ 4. Recherche MAC        │                    │
   │                                  │    dans devices.conf    │                    │
   │                                  │                         │                    │
   │                                  │ 5. MAC TROUVÉ?          │                    │
   │                                  │    Oui → OFFER IP       │                    │
   │                                  │    Non → NACK            │                    │
   │                                  │                         │                    │
   │◄──── 6. DHCP OFFER ──────────────│                         │    ◄─ Notif INFO  │
   │         (IP: 192.168.43.120)     │                         │      "Autorisé"   │
   │                                  │                         │                    │
   │─── 7. DHCP REQUEST ─────────────►│                         │                    │
   │                                  │ 8. Confirme & Sauve      │                    │
   │                                  │    dhcp_leases.conf      │                    │
   │◄──── 9. DHCP ACK ───────────────│                         │                    │
   │       (IP confirmé)              │                         │                    │
   │                                  │                         │                    │
   │ 10. IP configurée                │                         │                    │
   │     192.168.43.120               │                         │                    │
   │                                  │                         │                    │
   │───── 11. TCP Connect (5050) ────────────────────────────►│                    │
   │          MAC|IP                  │                         │                    │
   │                                  │                         │ 12. Vérifie IP    │
   │                                  │                         │     vs blocked_ips │
   │                                  │                         │                    │
   │                                  │                         │ 13. LOG connexion  │
   │                                  │                         │     Connexion.log  │◄─ Update
   │                                  │                         │                    │   Logs
   │◄──────────────────────────────── TCP Connected ─────────│                    │
   │                                  │                         │                    │
   │ 14. Client en ligne              │                         │                    │
   │     Accès Internet via AP        │                         │     ✓ Connecté     │
   │                                  │                         │                    │
```

---

## 📁 Flux des fichiers de configuration

```
┌─────────────────────────────────────────────┐
│ CONFIGURATION & DONNÉES PERSISTANTES         │
└─────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    
 ENTRÉE (Input)     TRAITEMENT          SORTIE (Logs)
       │                  │                   │
       │            ┌─────┴─────┐            │
       │            │           │            │
       ├─ devices.conf          │     ├─ Connexion.log
       │  (MAC|IP autorisés)    │     │  (Connexions TCP)
       │                        │     │
       ├─ users.conf            │     ├─ dhcp.log
       │  (username:hash)       │     │  (Allocations DHCP)
       │                        │     │
       ├─ server.conf           │     ├─ notifications.log
       │  (ports, interfaces)   │     │  (Notifs INFO/WARNING)
       │                        │     │
       └─ blocked_ips.conf      │     └─ dhcp_leases.conf
          (IPs bloquées)        │        (Historique leases)
                                │
                         SERVEURS
                         PYTHON
                    (DHCP + TCP + GUI)
```

---

## 🔄 Cycle de vie complet (Timeline)

```
TEMPS          ÉVÉNEMENT                          ÉTAT
────────────────────────────────────────────────────────────
T=0s      ► bash start_system.sh
          ► Vérification config système

T=2s      ► DHCP Server démarre (port 67)        🟢 ÉCOUTE
          ► En attente DHCP DISCOVER

T=3s      ► TCP Server démarre (port 5050)       🟢 ÉCOUTE
          ► En attente connexions clients

T=5s      ► GUI Frontend apparaît                 🖥️  AFFICHAGE
          ► Menu principal visible

T=10s     ► Client se connecte WiFi
          ► Envoie DHCP DISCOVER

T=10.5s   ► Serveur DHCP reçoit DISCOVER
          ► Cherche MAC dans devices.conf

T=11s     ► Serveur répond DHCP OFFER
          ► ou NACK selon authorization

T=11.5s   ► Client envoie DHCP REQUEST

T=12s     ► Serveur envoie DHCP ACK
          ► Sauve lease dans dhcp_leases.conf
          ► Génère notification

T=12.5s   ► Client configure IP
          ► Se connecte TCP port 5050

T=13s     ► Serveur TCP accepte/bloque
          ► Enregistre dans Connexion.log

T=15s     ► GUI met à jour logs & notifications
          ► Affiche l'appareil connecté

...
T=3600s   ► Lease expire (après 1 heure)
          ► Serveur DHCP libère IP
```

---

## 🔐 Flux de sécurité

```
┌─────────────────────────────────────────────────────────────┐
│ CONTRÔLE D'ACCÈS MULTICOUCHE                                │
└─────────────────────────────────────────────────────────────┘

COUCHE 1: DHCP (Allocation IP)
    ├─ Vérification MAC dans devices.conf
    ├─ SI MAC autorisé → Alloue IP + notification INFO
    └─ SI MAC inconnu → Refuse IP + notification WARNING

COUCHE 2: FILTRAGE IP (TCP Server)
    ├─ Vérifie IP dans blocked_ips.conf
    ├─ SI IP bloquée → Ferme connexion + log BLOCKED
    └─ SI IP autorisée → Accepte connexion + log CONNECTED

COUCHE 3: AUTHENTIFICATION (GUI)
    ├─ Username + Password (hashés dans users.conf)
    ├─ Accès contrôlé à gestion appareils
    └─ Actions loggées

RÉSULTAT: Triple protection ✓
```

---

## 📊 Résumé des flux

| **Flux** | **Direction** | **Port** | **Protocole** | **Rôle** |
|----------|--------------|---------|--------------|----------|
| Découverte réseau | Client → Serveur | 67 | DHCP | Allocation IP |
| Connexion clients | Client → Serveur | 5050 | TCP | Logs & gestion |
| Interface admin | Local | GUI | Tkinter | Contrôle système |
| Notifications | Backend → Frontend | IPC | Fichiers | Alertes temps réel |

---

## 🎯 Cas d'usage: Bloc Opératoire Complet

```
Scénario: 5 appareils se connectent simultanément

1. Device A (MAC: AA:BB:CC:DD:EE:01) ✓ AUTORISÉ
   → DHCP OFFER (192.168.43.100)
   → TCP Connect ✓
   → GUI: "Device A connecté" [INFO]

2. Device B (MAC: AA:BB:CC:DD:EE:02) ✓ AUTORISÉ
   → DHCP OFFER (192.168.43.101)
   → TCP Connect ✓
   → GUI: "Device B connecté" [INFO]

3. Device C (MAC: XX:YY:ZZ:AA:BB:CC) ✗ INCONNU
   → DHCP NACK
   → TCP Blocked
   → GUI: "Appareil inconnu XYZ" [WARNING]
   → admin peut ajouter à devices.conf

4. Device D (MAC: AA:BB:CC:DD:EE:03) ✓ AUTORISÉ
   → DHCP OFFER (192.168.43.102)
   → TCP Connect ✓
   → GUI: "Device D connecté" [INFO]

5. Device E (réessaye après blocage)
   → Même flux
   → Si MAC maintenant dans devices.conf → Autorisé

STATISTIQUES AFFICHÉES:
├─ Appareils connectés: 4/5
├─ Appareils bloqués: 1
└─ Notifications: [3 INFO, 2 WARNING]
```

---

## 💡 Points clés du flux

✅ **Architecture Client-Serveur**
- Serveur centralisé sur le PC (Point d'accès)
- Clients multiples (appareils WiFi)

✅ **Deux niveaux de service**
- DHCP pour allocation IP
- TCP pour gestion & monitoring

✅ **Sécurité multicouche**
- MAC filtering (DHCP)
- IP blocking (TCP)
- User authentication (GUI)

✅ **Persistence des données**
- Configurations persistantes (conf files)
- Logs archivés (log files)
- Notifications en temps réel

✅ **Interface intuitif**
- Tkinter GUI pour administration
- Dashboard unifiée
- Notifications visuelles
