#!/usr/bin/env python3
import sys
import os
import signal
import tkinter as tk
from tkinter import messagebox

# PATHS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))

sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

# Safe import
try:
    from config_manager import validate_credentials
except Exception:
    def validate_credentials(u, p):
        return u == "admin" and p == "admin123"

LogsView = None
CreateUserView = None
ListUserView = None
NotificationsView = None


def load_views():
    global LogsView, CreateUserView, ListUserView, NotificationsView
    if LogsView:
        return
    try:
        from frontend.views.logs_view import LogsView
    except Exception as e:
        print("[WARN] LogsView:", e)
    try:
        from frontend.views.users.list_user_view import ListUserView
    except Exception as e:
        print("[WARN] ListUserView:", e)
    try:
        from frontend.views.users.create_user_view import CreateUserView
    except Exception as e:
        print("[WARN] CreateUserView:", e)
    try:
        from frontend.views.notifications_view import NotificationsView
    except Exception as e:
        print("[WARN] NotificationsView:", e)


class NavigationController:
    def __init__(self, container):
        self.container = container
        self.current_view = None

    def clear(self):
        if self.current_view and hasattr(self.current_view, "on_destroy"):
            self.current_view.on_destroy()
        for w in self.container.winfo_children():
            w.destroy()

    def show_logs(self):
        self.clear()
        self.current_view = LogsView(self.container)
        self.current_view.pack(fill="both", expand=True)

    def show_users(self):
        self.clear()
        self.current_view = ListUserView(self.container, self)
        self.current_view.pack(fill="both", expand=True)

    def show_notifications(self):
        self.clear()
        self.current_view = NotificationsView(self.container)
        self.current_view.pack(fill="both", expand=True)


def open_home_page(root):
    load_views()
    root.withdraw()

    home = tk.Toplevel(root)
    home.title("Page d'accueil")
    home.geometry("700x450")

    nav = tk.Frame(home, bg="#4a90e2", height=50)
    nav.pack(fill="x")

    content = tk.Frame(home, bg="#f5f5f5")
    content.pack(fill="both", expand=True)

    controller = NavigationController(content)

    tk.Button(nav, text="Gestion des Logs",
              command=controller.show_logs,
              bg="#60a5fa", fg="white").pack(side="left", padx=10, pady=5)

    tk.Button(nav, text="Gestion des Utilisateurs",
              command=controller.show_users,
              bg="#60a5fa", fg="white").pack(side="left", padx=10, pady=5)

    tk.Button(nav, text="Notifications",
              command=controller.show_notifications,
              bg="#60a5fa", fg="white").pack(side="left", padx=10, pady=5)

    tk.Label(home, text="Bienvenue sur la page d'accueil!",
             font=("Arial", 16)).pack(pady=10)

    def logout():
        controller.clear()
        home.destroy()
        root.deiconify()

    tk.Button(home, text="Déconnexion",
              command=logout,
              bg="#ff6b6b", fg="white").pack(pady=10)


def main():
    def signal_handler(*_):
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    root = tk.Tk()
    root.title("Connexion")
    root.geometry("500x400")

    frame = tk.Frame(root)
    frame.pack(expand=True)

    tk.Label(frame, text="Nom d'utilisateur").pack()
    user = tk.Entry(frame)
    user.pack()

    tk.Label(frame, text="Mot de passe").pack()
    pwd = tk.Entry(frame, show="•")
    pwd.pack()

    def login():
        if validate_credentials(user.get(), pwd.get()):
            open_home_page(root)
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects")

    tk.Button(frame, text="Connexion", command=login).pack(pady=10)
    root.mainloop()


if __name__ == "__main__":
    main()
