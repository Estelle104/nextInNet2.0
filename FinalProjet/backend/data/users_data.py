"""
Module pour charger les utilisateurs depuis la configuration
Au lieu d'avoir les données en dur, on les charge du fichier config/users.conf
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_manager import get_users

# Charger les utilisateurs depuis la configuration
_user_dict = get_users()
users = [
    {"username": username, "password": password}
    for username, password in _user_dict.items()
]
