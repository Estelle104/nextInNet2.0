import tkinter as tk
from tkinter import font
import sys
import os
import threading

# Déterminer le répertoire racine du projet
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))

# Ajout du répertoire racine du projet au chemin Python
sys.path.insert(0, PROJECT_ROOT)

# Import des pages (Views)
from FinalProjet.frontend.views.create_user_view import CreateUserView
from FinalProjet.frontend.views.list_user_view import ListUserView
from FinalProjet.frontend.views.logs_view import LogsView
from FinalProjet.frontend.views.notifications_view import NotificationsView


class App(tk.Tk):
    """
    Classe principale de l'application.
    Elle hérite de Tk (fenêtre principale).
    """

    def __init__(self):
        super().__init__()

        # ----- Configuration de la fenêtre -----
        self.title("NextInNet - Gestion Réseau")
        self.geometry("900x650")
        self.resizable(True, True)

        # Thème moderne avec dégradé subtil
        self.configure(bg="#f5f7fa")

        # ----- Polices personnalisées -----
        self.title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.button_font = font.Font(family="Segoe UI", size=10)
        self.body_font = font.Font(family="Segoe UI", size=9)

        # ----- En-tête de l'application -----
        header = tk.Frame(self, bg="#2c3e50", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title_label = tk.Label(
            header,
            text="🌐 NextInNet - Gestion du Point d'Accès",
            font=self.title_font,
            bg="#2c3e50",
            fg="white",
            pady=15
        )
        title_label.pack(side="left", padx=20)

        # ----- Barre de navigation avec notifications -----
        nav_frame = tk.Frame(self, bg="#ffffff", height=60)
        nav_frame.pack(fill="x", side="top")
        nav_frame.pack_propagate(False)

        # Boutons de navigation
        button_frame = tk.Frame(nav_frame, bg="#ffffff")
        button_frame.pack(side="left", padx=10, pady=10)

        self.nav_buttons = {}
        for page_name in ["👤 Utilisateurs", "📋 Logs", "🔔 Notifications"]:
            btn = tk.Button(
                button_frame,
                text=page_name,
                font=self.button_font,
                bg="#4a90e2",
                fg="white",
                padx=15,
                pady=8,
                relief="flat",
                cursor="hand2",
                command=lambda pn=page_name: self.on_nav_click(pn)
            )
            btn.pack(side="left", padx=5)
            self.nav_buttons[page_name] = btn

        # Notification counter (côté droit)
        self.notif_counter_label = tk.Label(
            nav_frame,
            text="🔔 0",
            font=("Segoe UI", 12, "bold"),
            bg="#ffffff",
            fg="#4a90e2"
        )
        self.notif_counter_label.pack(side="right", padx=20, pady=10)

        # ----- Conteneur principal pour les vues -----
        self.container = tk.Frame(self, bg="#f5f7fa")
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.current_page = None
        
        # Créer toutes les pages
        for F, page_name in [(CreateUserView, "CreateUserView"), 
                              (ListUserView, "ListUserView"),
                              (LogsView, "LogsView"),
                              (NotificationsView, "NotificationsView")]:
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("CreateUserView")
        
        # Démarrer la mise à jour du compteur de notifications
        self.start_notification_counter()

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        self.current_page = page_name
    
    def on_nav_click(self, nav_text):
        """Gère les clics sur les boutons de navigation"""
        # Mapper le texte du bouton aux noms de frames
        mapping = {
            "👤 Utilisateurs": "ListUserView",
            "📋 Logs": "LogsView",
            "🔔 Notifications": "NotificationsView"
        }
        
        page_name = mapping.get(nav_text, "CreateUserView")
        self.show_frame(page_name)
    
    def start_notification_counter(self):
        """Démarre le thread de mise à jour du compteur de notifications"""
        def update_counter():
            while True:
                try:
                    warnings, blocked = self.get_unread_notifications()
                    
                    # Mettre à jour le label
                    total = warnings + blocked
                    if total > 0:
                        color = "#EF5350" if blocked > 0 else "#FFB74D"  # Rouge si bloqué, sinon orange
                        self.notif_counter_label.config(
                            text=f"🔔 {total}",
                            fg=color
                        )
                    else:
                        self.notif_counter_label.config(
                            text="🔔 0",
                            fg="#4a90e2"
                        )
                    
                    threading.Event().wait(2)  # Mettre à jour toutes les 2 secondes
                except:
                    pass
        
        counter_thread = threading.Thread(target=update_counter, daemon=True)
        counter_thread.start()
    
    def get_unread_notifications(self):
        """Compte les notifications WARNING et BLOCKED"""
        notifications_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "backend", "logs", "notifications.log"
        )
        
        warnings = 0
        blocked = 0
        
        try:
            if os.path.exists(notifications_file):
                with open(notifications_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if "[WARNING]" in line:
                            warnings += 1
                        elif "[BLOCKED]" in line:
                            blocked += 1
        except:
            pass
        
        return warnings, blocked

