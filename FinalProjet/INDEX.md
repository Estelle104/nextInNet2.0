# 📑 INDEX - Accès facile aux ressources de test

## 🎯 Où commencer?

### Je veux tester rapidement (5 min)
👉 Lire: [TEST_INSTRUCTIONS.md](TEST_INSTRUCTIONS.md#option-1-test-complet-en-une-commande-)

### Je veux lancer l'application (2 min)
👉 Lire: [TEST_INSTRUCTIONS.md](TEST_INSTRUCTIONS.md#option-2-démarrage-automatique-)

### Je veux tester manuellement (30 min)
👉 Lire: [GUIDE_TEST.md](GUIDE_TEST.md)

### Je veux tous les détails techniques
👉 Lire: [README_TESTS.md](README_TESTS.md)

---

## 📋 Tous les fichiers de test

### Documentation principale
| Fichier | Description | Temps |
|---------|-------------|-------|
| [TEST_INSTRUCTIONS.md](TEST_INSTRUCTIONS.md) | **À LIRE EN PREMIER** | 5 min |
| [GUIDE_TEST.md](GUIDE_TEST.md) | Guide complet détaillé | 30 min |
| [README_TESTS.md](README_TESTS.md) | Résumé et architecture | 10 min |
| [FILES_DISPONIBLES.md](FILES_DISPONIBLES.md) | Index des fichiers | 5 min |

### Scripts de test exécutables
| Script | Location | Temps |
|--------|----------|-------|
| **quick_test.sh** | `/FinalProjet/` | 10 sec |
| **start.sh** | `/FinalProjet/` | 5 min |
| test_config.sh | `/FinalProjet/backend/scripts/` | 30 sec |
| test_socket_communication.sh | `/FinalProjet/backend/scripts/` | 2 min |
| run_all_tests.sh | `/FinalProjet/backend/scripts/` | 5 min |

### Référence rapide
| Fichier | Description |
|---------|------------|
| [REFERENCE_RAPIDE.sh](REFERENCE_RAPIDE.sh) | Commandes en copier-coller |
| [INDEX.md](INDEX.md) | Vous êtes ici! |

---

## 🚀 Parcours d'apprentissage recommandé

### Niveau 1: Débutant (15 minutes)

```
1. Lire: TEST_INSTRUCTIONS.md (Option 1)
2. Lancer: bash quick_test.sh
3. Lancer: bash start.sh
4. Tester dans l'interface GUI
```

**Résultat:** Vous savez que tout fonctionne ✓

### Niveau 2: Intermédiaire (45 minutes)

```
1. Lire: GUIDE_TEST.md
2. Lancer: test_config.sh
3. Lancer: test_socket_communication.sh
4. Tester manuellement le serveur
5. Consulter: REFERENCE_RAPIDE.sh
```

**Résultat:** Vous comprenez l'architecture ✓

### Niveau 3: Avancé (2 heures)

```
1. Lire: README_TESTS.md
2. Lancer: run_all_tests.sh
3. Lire: backend/config/README_CONFIG.md
4. Lire: backend/scripts/README_SOCKET.md
5. Parcourir le code source
```

**Résultat:** Vous pouvez modifier le projet ✓

---

## 📍 Structure des répertoires

```
/FinalProjet/
├── 📄 README_TESTS.md          ← Résumé complet
├── 📄 TEST_INSTRUCTIONS.md     ← À LIRE EN PREMIER
├── 📄 GUIDE_TEST.md            ← Tests détaillés
├── 📄 FILES_DISPONIBLES.md     ← Index des fichiers
├── 📄 REFERENCE_RAPIDE.sh      ← Commandes en copier-coller
├── 📄 INDEX.md                 ← Vous êtes ici
├── 🚀 quick_test.sh            ← Test rapide
├── 🚀 start.sh                 ← Démarrage complet
│
├── backend/
│   ├── config/
│   │   ├── server.conf         ← Configuration serveur
│   │   ├── users.conf          ← Utilisateurs
│   │   ├── logging.conf        ← Logging
│   │   └── README_CONFIG.md    ← Doc configuration
│   ├── scripts/
│   │   ├── socket_server.sh    ← Serveur socket
│   │   ├── socket_client.sh    ← Client socket
│   │   ├── test_config.sh      ← Test configuration
│   │   ├── test_socket_communication.sh
│   │   ├── run_all_tests.sh    ← Tous les tests
│   │   └── README_SOCKET.md    ← Doc socket
│   ├── serveur/
│   │   └── log_server.py       ← Serveur logs
│   ├── client/
│   │   └── client.py           ← Client GUI
│   └── config_manager.py       ← Gestionnaire config
│
└── frontend/
    └── views/
        ├── logs_view.py        ← Affichage logs
        └── ...
```

---

## 🎓 Cas d'usage

### Cas 1: Je veux juste tester que ça marche
```bash
bash /FinalProjet/quick_test.sh
```
Résultat: ✓ ou ✗

### Cas 2: Je veux utiliser l'application
```bash
bash /FinalProjet/start.sh
```
Puis: Se connecter avec admin / admin123

### Cas 3: Je veux tester un composant spécifique
```bash
# Configuration
bash /FinalProjet/backend/scripts/test_config.sh

# Socket
bash /FinalProjet/backend/scripts/test_socket_communication.sh
```

### Cas 4: Je veux ajouter des logs de test
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/path/to/backend')
from serveur.log_server import log_entry
log_entry("192.168.1.100", "AA:BB:CC:DD:EE:FF")
EOF
```

### Cas 5: Je veux modifier la configuration
```bash
# Éditer le port
nano /FinalProjet/backend/config/server.conf

# Éditer les utilisateurs
nano /FinalProjet/backend/config/users.conf
```

---

## 🔗 Références rapides

### Commandes d'une ligne

```bash
# Test rapide
cd /FinalProjet && bash quick_test.sh

# Démarrer l'app
cd /FinalProjet && bash start.sh

# Récupérer les logs actuels
bash /FinalProjet/backend/scripts/socket_client.sh 127.0.0.1 5050 realtime 5

# Voir tous les logs
bash /FinalProjet/backend/scripts/socket_client.sh 127.0.0.1 5050 history 5
```

---

## 📊 Matrix de test

| Composant | Test | Fichier | Status |
|-----------|------|---------|--------|
| Configuration | test_config.sh | backend/scripts/ | ✓ |
| Socket | test_socket_communication.sh | backend/scripts/ | ✓ |
| Serveur | test manuel | GUIDE_TEST.md | ✓ |
| Client GUI | test manuel | GUIDE_TEST.md | ✓ |
| Logs temps réel | test manuel | GUIDE_TEST.md | ✓ |
| Navigation | test manuel | GUIDE_TEST.md | ✓ |

---

## 🆘 Besoin d'aide?

1. **Erreur pendant quick_test.sh?**
   → Voir GUIDE_TEST.md > Dépannage

2. **Pas de logs qui s'affichent?**
   → Voir TEST_INSTRUCTIONS.md > Erreurs

3. **Port déjà utilisé?**
   → Voir REFERENCE_RAPIDE.sh > SECTION 5

4. **Je ne sais pas par où commencer**
   → Lire TEST_INSTRUCTIONS.md en premier

---

## ✅ Checklist avant d'utiliser

- [ ] Lire TEST_INSTRUCTIONS.md
- [ ] Lancer quick_test.sh avec succès
- [ ] Lancer start.sh avec succès
- [ ] Se connecter dans l'interface GUI
- [ ] Vérifier que les logs s'affichent

---

## 📝 Notes

- Tous les chemins sont **absolus** (vous pouvez les copier partout)
- Les fichiers bash sont **exécutables** (chmod +x fait automatiquement)
- La documentation est en **Markdown** (ouvrez-la dans VS Code)
- Les tests ne modifient **rien** (sauf ajouter des logs de test)

---

## 🎉 Vous êtes prêt!

### Étape 1: Lire
👉 [TEST_INSTRUCTIONS.md](TEST_INSTRUCTIONS.md)

### Étape 2: Lancer
```bash
bash quick_test.sh
```

### Étape 3: Tester
```bash
bash start.sh
```

---

**Bienvenue dans FinalProjet!** 🚀

*Dernière mise à jour: 20 janvier 2026*
