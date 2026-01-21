#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import os
import sys

# Déterminer les répertoires
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BACKEND_DIR))

# Ajouter tous les répertoires nécessaires au path
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Imports sécurisés
try:
    from config_manager import validate_credentials
except ImportError:
    # Si config_manager n'existe pas, utiliser une fonction simple
    def validate_credentials(username, password):
        """Valide les identifiants (fallback)"""
        return username == "admin" and password == "admin123"

try:
    from frontend.views.logs_view import LogsView
    from frontend.views.users.create_user_view import CreateUserView
    from frontend.views.users.list_user_view import ListUserView
    from frontend.views.notifications_view import NotificationsView
except Exception as e:
    print(f"[ERROR] Impossible d'importer les vues: {e}", file=sys.stderr)
    sys.exit(1)

class NavigationController:
    """Controller for managing view navigation"""
    def __init__(self, content_frame):
        self.content_frame = content_frame
    
    def show_frame(self, frame_class_name):
        """Show the specified frame"""
        try:
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            if frame_class_name == "CreateUserView":
                CreateUserView(self.content_frame, self).pack(fill="both", expand=True)
            elif frame_class_name == "ListUserView":
                ListUserView(self.content_frame, self).pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'afficher la vue: {e}")

def open_home_page(fenetre):
    """Ouvre la page d'accueil après connexion"""
    try:
        fenetre.destroy()
        home_window = tk.Tk()
        home_window.title("Page d'accueil")
        home_window.geometry("600x400")

        # Navigation bar
        nav_frame = tk.Frame(home_window, bg="#4a90e2", height=50)
        nav_frame.pack(fill="x")

        # Create content frame first
        content_frame = tk.Frame(home_window, bg="#f5f5f5")
        content_frame.pack(fill="both", expand=True)

        # Create controller
        controller = NavigationController(content_frame)

        def show_logs():
            try:
                for widget in content_frame.winfo_children():
                    widget.destroy()
                LogsView(content_frame).pack(fill="both", expand=True)
            except Exception as e:
                messagebox.showerror("Erreur Logs", f"Erreur: {str(e)[:100]}")

        def show_users():
            try:
                controller.show_frame("ListUserView")
            except Exception as e:
                messagebox.showerror("Erreur Utilisateurs", f"Erreur: {str(e)[:100]}")

        def show_notifications():
            try:
                for widget in content_frame.winfo_children():
                    widget.destroy()
                NotificationsView(content_frame).pack(fill="both", expand=True)
            except Exception as e:
                messagebox.showerror("Erreur Notifications", f"Erreur: {str(e)[:100]}")

        tk.Button(nav_frame, text="Gestion des Logs", command=show_logs, bg="#60a5fa", fg="white").pack(side="left", padx=10, pady=5)
        tk.Button(nav_frame, text="Gestion des Utilisateurs", command=show_users, bg="#60a5fa", fg="white").pack(side="left", padx=10, pady=5)
        tk.Button(nav_frame, text="Notifications", command=show_notifications, bg="#60a5fa", fg="white").pack(side="left", padx=10, pady=5)

        tk.Label(home_window, text="Bienvenue sur la page d'accueil!", font=("Arial", 16)).pack(pady=20)

        tk.Button(home_window, text="Déconnexion", command=home_window.destroy, bg="#ff6b6b", fg="white", font=("Arial", 10, "bold"), width=12).pack(pady=10)

        home_window.mainloop()
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur page d'accueil: {str(e)}")

def valider_login(fenetre, entry_username, entry_password):
    """Valide les identifiants de connexion"""
    try:
        username = entry_username.get()
        password = entry_password.get()
        
        if username == "" or password == "":
            messagebox.showwarning("Champs vides", "Veuillez remplir tous les champs")
        elif validate_credentials(username, password):
            messagebox.showinfo("Succès", f"Bienvenue {username}!")
            open_home_page(fenetre)
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur validation: {str(e)}")

def quitter(fenetre):
    """Ferme l'application"""
    try:
        fenetre.destroy()
    except:
        sys.exit(0)

def main():
    """Fonction principale - Lance l'écran de connexion"""
    try:
        fenetre = tk.Tk()
        fenetre.title("Login - Connexion Serveur")
        fenetre.geometry("500x450")
        fenetre.resizable(False, False)
        fenetre.configure(bg="#ced4da")

        # Frame principal avec un style moderne
        main_frame = tk.Frame(fenetre, bg="#adb5bd", bd=2, relief="raised")
        main_frame.pack(pady=30, padx=30, fill="both", expand=True)

        # Titre
        titre = tk.Label(main_frame, text="CONNEXION AU SERVEUR", 
                         font=("Arial", 20, "bold"), 
                         bg="#adb5bd", fg="#1a252f")
        titre.pack(pady=(20, 10))

        # Frame pour les champs
        input_frame = tk.Frame(main_frame, bg="#adb5bd")
        input_frame.pack(pady=10, padx=20)

        # Username
        tk.Label(input_frame, text="Nom d'utilisateur:", 
                 font=("Arial", 12), 
                 bg="#adb5bd", fg="#1a252f").grid(row=0, column=0, sticky="w", pady=5)
        entry_username = tk.Entry(input_frame, font=("Arial", 11), width=23)
        entry_username.grid(row=0, column=1, pady=5, padx=10)

        # Password
        tk.Label(input_frame, text="Mot de passe:", 
                 font=("Arial", 12), 
                 bg="#adb5bd", fg="#1a252f").grid(row=1, column=0, sticky="w", pady=5)
        entry_password = tk.Entry(input_frame, font=("Arial", 11), 
                                 show="•", width=23)
        entry_password.grid(row=1, column=1, pady=5, padx=10)

        # Boutons
        button_frame = tk.Frame(main_frame, bg="#adb5bd")
        button_frame.pack(pady=20)

        btn_login = tk.Button(button_frame, text="Se connecter", 
                             command=lambda: valider_login(fenetre, entry_username, entry_password),
                             bg="#3498db", fg="white",
                             font=("Arial", 10, "bold"),
                             width=12, height=1,
                             cursor="hand2")
        btn_login.pack(side="left", padx=5)

        btn_quit = tk.Button(button_frame, text="Quitter", 
                            command=lambda: quitter(fenetre),
                            bg="#ff6b6b", fg="white",
                            font=("Arial", 10, "bold"),
                            width=12, height=1,
                            cursor="hand2")
        btn_quit.pack(side="left", padx=5)

        # Focus sur le premier champ
        entry_username.focus()

        # Lier la touche Entrée à la validation
        fenetre.bind('<Return>', lambda event: valider_login(fenetre, entry_username, entry_password))

        # Lancer l'application
        fenetre.mainloop()
    except Exception as e:
        print(f"[FATAL ERROR] {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"[FATAL] {str(e)}", file=sys.stderr)
        sys.exit(1)
