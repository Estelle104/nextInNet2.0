import tkinter as tk
from tkinter import messagebox
import sys
import os

# Ajouter le chemin du backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
from config_manager import add_user

BG_COLOR = "#eaf2fb"
BTN_COLOR = "#1e88e5"
BTN_HOVER = "#1565c0"
TEXT_COLOR = "#0d47a1"

class CreateUserView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Titre
        title = tk.Label(
            self,
            text="Créer un Utilisateur",
            font=("Arial", 18, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title.pack(pady=20)

        # Username
        tk.Label(
            self,
            text="Nom d'utilisateur",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 11)
        ).pack()

        self.username_entry = tk.Entry(self, width=30, font=("Arial", 11))
        self.username_entry.pack(pady=5)

        # Password
        tk.Label(
            self,
            text="Mot de passe",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 11)
        ).pack(pady=(20, 0))

        self.password_entry = tk.Entry(self, show="*", width=30, font=("Arial", 11))
        self.password_entry.pack(pady=5)

        # Confirm Password
        tk.Label(
            self,
            text="Confirmer le mot de passe",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 11)
        ).pack(pady=(20, 0))

        self.password_confirm_entry = tk.Entry(self, show="*", width=30, font=("Arial", 11))
        self.password_confirm_entry.pack(pady=5)

        # Status label
        self.status_label = tk.Label(
            self,
            text="",
            bg=BG_COLOR,
            fg="#d32f2f",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=10)

        # Bouton créer
        create_button = tk.Button(
            self,
            text="Créer l'utilisateur",
            bg=BTN_COLOR,
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.create_user,
            padx=20,
            pady=10
        )
        create_button.pack(pady=20)

        # Navigation vers ListUserView
        nav_button = tk.Button(
            self,
            text="Voir la liste des utilisateurs",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            command=lambda: controller.show_frame("ListUserView"),
            padx=20,
            pady=10
        )
        nav_button.pack(pady=10)

    def create_user(self):
        """Crée un nouvel utilisateur"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        password_confirm = self.password_confirm_entry.get()

        # Validations
        if not username or not password:
            self.status_label.config(text="❌ Remplissez tous les champs", fg="#d32f2f")
            return

        if len(username) < 3:
            self.status_label.config(text="❌ Username minimum 3 caractères", fg="#d32f2f")
            return

        if password != password_confirm:
            self.status_label.config(text="❌ Les mots de passe ne correspondent pas", fg="#d32f2f")
            return

        # Ajouter l'utilisateur
        success, message = add_user(username, password)

        if success:
            self.status_label.config(text=f"✓ {message}", fg="#4CAF50")
            # Vider les champs
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.password_confirm_entry.delete(0, tk.END)
            # Rafraîchir la liste
            self.controller.frames["ListUserView"].load_users()
        else:
            self.status_label.config(text=f"❌ {message}", fg="#d32f2f")
