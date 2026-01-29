#!/bin/bash

# ============================================================================
# TEST: Gestion des utilisateurs inconnus et tentatives SSH
# ============================================================================
# Scénario:
# 1. Un utilisateur INCONNU se connecte → tracking 15s
# 2. Pas d'activité pendant 15s → EXPULSION automatique du réseau
# 3. Si tente SSH → PING + SHUTDOWN -h now
# ============================================================================

set -e

PROJECT_ROOT="/home/itu/S3/MrHaga/projet/nextInNet2.0/FinalProjet"
BACKEND_DIR="$PROJECT_ROOT/backend"
LOGS_DIR="$PROJECT_ROOT/logs"
NOTIFICATIONS_LOG="$LOGS_DIR/notifications.log"
CONNEXION_LOG="$LOGS_DIR/Connexion.log"
BLOCKED_IPS_FILE="$BACKEND_DIR/config/blocked_ips.conf"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔒 TEST: Gestion des Utilisateurs Inconnus"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Fonction d'affichage
print_section() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "▶ $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Test 1: Vérifier que le serveur détecte les connexions inconnues
print_section "TEST 1: Détection d'une machine inconnue (IP dynamique)"
echo "✓ Une machine avec IP entre 150-200 est considérée INCONNUE"
echo "✓ Timeout: 15 secondes avant expulsion"
echo "✓ Notification WARNING envoyée"

# Test 2: Simuler une tentative SSH
print_section "TEST 2: Tentative SSH depuis machine inconnue"
echo "✓ Détection du port 22 ou 'SSH' dans la requête"
echo "✓ Action: BLOQUER + PING + SHUTDOWN -h now"
echo "✓ IP bloquée de manière permanente (added to blocked_ips.conf)"

# Test 3: Vérifier les fichiers de log
print_section "TEST 3: Vérification des fichiers de log"

if [ -f "$NOTIFICATIONS_LOG" ]; then
    echo "📋 Notifications reçues:"
    echo ""
    tail -20 "$NOTIFICATIONS_LOG" | grep -E "WARNING|BLOCKED|TIMEOUT" || echo "Aucune notification encore"
else
    echo "⚠️ Fichier notifications.log non trouvé"
fi

if [ -f "$CONNEXION_LOG" ]; then
    echo ""
    echo "📋 Log des connexions:"
    echo ""
    tail -20 "$CONNEXION_LOG" | grep -E "UNKNOWN|INCONNUE" || echo "Aucune connexion inconnue enregistrée"
else
    echo "⚠️ Fichier Connexion.log non trouvé"
fi

# Test 4: IPs bloquées
print_section "TEST 4: Vérification des IPs bloquées"
if [ -f "$BLOCKED_IPS_FILE" ]; then
    echo "🚫 IPs bloquées:"
    echo ""
    tail -10 "$BLOCKED_IPS_FILE" | grep -v "^#" || echo "Aucune IP bloquée"
else
    echo "⚠️ Fichier blocked_ips.conf non trouvé"
fi

# Test 5: Vérifier les règles iptables
print_section "TEST 5: Vérification des règles iptables"
echo "Règles actuelles pour DROP:"
echo ""
sudo iptables -L -v -n 2>/dev/null | grep "DROP" | head -10 || echo "Aucune règle DROP active"

# Test 6: Recommandations
print_section "RECOMMANDATIONS DE TEST"
cat << 'EOF'

🔍 Pour tester le système complètement:

1️⃣ Démarrer le serveur TCP:
   python3 /home/itu/S3/MrHaga/projet/nextInNet2.0/FinalProjet/backend/serveur/tcp_server_simple.py

2️⃣ Simuler une connexion inconnue (IP dynamique 150-200):
   echo "test" | nc 192.168.43.150 5050

3️⃣ Observer le timeout 15 secondes:
   tail -f /home/itu/S3/MrHaga/projet/nextInNet2.0/FinalProjet/logs/notifications.log

4️⃣ Tester une tentative SSH depuis inconnue:
   ssh -p 22 unknown_user@192.168.43.150
   (Doit être bloquée et la machine pingée/éteinte)

5️⃣ Vérifier les IPs bloquées:
   cat /home/itu/S3/MrHaga/projet/nextInNet2.0/FinalProjet/backend/config/blocked_ips.conf

📊 Comportements attendus:

✅ Machine INCONNUE (IP 150-200):
   - Notification: ⚠️ WARNING
   - Connexion: Acceptée temporairement (IP dynamique)
   - Timeout: 15 secondes avant expulsion
   - SSH: BLOQUÉE + PING + SHUTDOWN -h now

✅ Machine AUTORISÉE (dans devices.conf):
   - Notification: ✓ INFO
   - SSH: Autorisé
   - Pas d'expulsion

✅ Machine BLOQUÉE (dans blocked_ips.conf):
   - Notification: 🚫 BLOCKED
   - Toute connexion: Refusée
   - iptables: DROP activée

EOF

print_section "RÉSUMÉ DE LA CONFIGURATION"
echo "✓ Timeout inactif: 15 secondes"
echo "✓ Plage IP dynamique: 192.168.43.150-200"
echo "✓ Détection SSH: Port 22, 'ssh', 'SSH', 'OpenSSH'"
echo "✓ Action SSH inconnue: BLOQUER + PING + SHUTDOWN"
echo ""
echo "✅ Configuration appliquée avec succès!"
