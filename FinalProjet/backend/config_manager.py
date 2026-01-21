"""
Module de gestion des configurations
Charge les fichiers de configuration et les expose globalement
"""

import os
import configparser
from pathlib import Path

# Déterminer le répertoire de configuration
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")

class ConfigManager:
    """Gestionnaire centralisé de configurations"""
    
    def __init__(self):
        self.server_config = self._load_config("server.conf")
        self.users_config = self._load_users("users.conf")
        self.logging_config = self._load_config("logging.conf")
    
    def _load_config(self, filename):
        """Charge un fichier de configuration .conf"""
        config = {}
        config_path = os.path.join(CONFIG_DIR, filename)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Ignorer les commentaires et lignes vides
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        except FileNotFoundError:
            print(f"[WARNING] Configuration file not found: {config_path}")
        except Exception as e:
            print(f"[ERROR] Error loading config {filename}: {e}")
        
        return config
    
    def _load_users(self, filename):
        """Charge le fichier des utilisateurs"""
        users = {}
        config_path = os.path.join(CONFIG_DIR, filename)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Ignorer les commentaires et lignes vides
                    if not line or line.startswith('#'):
                        continue
                    
                    if ':' in line:
                        username, password = line.split(':', 1)
                        users[username.strip()] = password.strip()
        except FileNotFoundError:
            print(f"[WARNING] Users file not found: {config_path}")
        except Exception as e:
            print(f"[ERROR] Error loading users: {e}")
        
        return users
    
    def _load_devices(self, filename):
        """Charge le fichier des appareils (IP|MAC)"""
        devices = []
        config_path = os.path.join(CONFIG_DIR, filename)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Ignorer les commentaires et lignes vides
                    if not line or line.startswith('#'):
                        continue
                    
                    if '|' in line:
                        ip, mac = line.split('|', 1)
                        devices.append({
                            'ip': ip.strip(),
                            'mac': mac.strip()
                        })
        except FileNotFoundError:
            print(f"[WARNING] Devices file not found: {config_path}")
        except Exception as e:
            print(f"[ERROR] Error loading devices: {e}")
        
        return devices
    
    def add_device(self, ip, mac):
        """Ajoute un nouvel appareil"""
        # Ajouter à la liste en mémoire
        self.devices.append({'ip': ip, 'mac': mac})
        
        # Persister dans le fichier
        config_path = os.path.join(CONFIG_DIR, "devices.conf")
        try:
            with open(config_path, 'a', encoding='utf-8') as f:
                f.write(f"{ip}|{mac}\n")
            return True
        except Exception as e:
            print(f"[ERROR] Error adding device: {e}")
            return False
    
    def get_devices(self):
        """Retourne la liste des appareils"""
        if not hasattr(self, 'devices'):
            self.devices = self._load_devices("devices.conf")
        return self.devices
    
    def get_server_config(self, key, default=None):
        """Récupère une valeur de configuration serveur"""
        return self.server_config.get(key, default)
    
    def get_logging_config(self, key, default=None):
        """Récupère une valeur de configuration logging"""
        return self.logging_config.get(key, default)
    
    def get_users(self):
        """Retourne le dictionnaire des utilisateurs"""
        return self.users_config
    
    def validate_user(self, username, password):
        """Valide les credentials d'un utilisateur"""
        return self.users_config.get(username) == password

# Instance globale
config_manager = ConfigManager()

# Fonctions helper
def get_log_port():
    """Récupère le port de log"""
    return int(config_manager.get_server_config('LOG_PORT', '5050'))

def get_log_file():
    """Récupère le chemin du fichier de log"""
    log_dir = config_manager.get_server_config('LOG_DIRECTORY', './logs')
    log_file = config_manager.get_server_config('LOG_FILE', 'Connexion.log')
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, log_file)

def get_max_realtime_logs():
    """Récupère le nombre maximum de logs en temps réel"""
    return int(config_manager.get_server_config('MAX_REALTIME_LOGS', '10'))

def get_users():
    """Récupère tous les utilisateurs"""
    return config_manager.get_users()

def validate_credentials(username, password):
    """Valide les credentials"""
    return config_manager.validate_user(username, password)

def add_device(ip, mac):
    """Ajoute un nouvel appareil (IP et adresse MAC)"""
    return config_manager.add_device(ip, mac)

def get_devices():
    """Récupère tous les appareils"""
    return config_manager.get_devices()

