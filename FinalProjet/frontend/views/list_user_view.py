import sys
import os
import tkinter as tk
from tkinter import messagebox, ttk

# Déterminer le répertoire backend
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "..", "backend")
sys.path.insert(0, BACKEND_DIR)
from config_manager import get_users, delete_user

BG_COLOR = "#eaf2fb"
BTN_COLOR = "#1e88e5"
BTN_DELETE = "#d32f2f"
TEXT_COLOR = "#0d47a1"

class ListUserView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Titre
        title = tk.Label(
            self,
            text="Liste des Utilisateurs",
            font=("Arial", 18, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title.pack(pady=20)

        # Frame pour la liste avec scrollbar
        list_frame = tk.Frame(self, bg=BG_COLOR)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        # Listbox pour afficher les utilisateurs
        self.list_box = tk.Listbox(
            list_frame,
            width=50,
            height=15,
            font=("Arial", 10),
            yscrollcommand=scrollbar.set
        )
        self.list_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.list_box.yview)

        # Bind double-click pour supprimer
        self.list_box.bind("<Double-Button-1>", self.on_user_selected)

        # Status label
        self.status_label = tk.Label(
            self,
            text="Double-cliquez pour supprimer un utilisateur",
            bg=BG_COLOR,
            fg="#666666",
            font=("Arial", 9, "italic")
        )
        self.status_label.pack(pady=5)

        # Frame pour les boutons
        button_frame = tk.Frame(self, bg=BG_COLOR)
        button_frame.pack(fill="x", padx=20, pady=10)

        # Bouton rafraîchir
        refresh_button = tk.Button(
            button_frame,
            text="🔄 Rafraîchir",
            bg=BTN_COLOR,
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.load_users,
            padx=15
        )
        refresh_button.pack(side="left", padx=5)

        # Bouton créer
        create_button = tk.Button(
            button_frame,
            text="➕ Créer",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            command=lambda: controller.show_frame("CreateUserView"),
            padx=15
        )
        create_button.pack(side="left", padx=5)

        # Premier chargement
        self.load_users()

    def load_users(self):
        """Affiche les utilisateurs existants"""
        self.list_box.delete(0, tk.END)

        users_dict = get_users()

        if not users_dict:
            self.list_box.insert(tk.END, "Aucun utilisateur")
            self.status_label.config(text="✓ Aucun utilisateur créé", fg="#666666")
            return

        for username in users_dict.keys():
            self.list_box.insert(tk.END, f"👤 {username}")

        count = len(users_dict)
        self.status_label.config(
            text=f"✓ {count} utilisateur(s) | Double-cliquez pour supprimer",
            fg="#4CAF50"
        )

    def on_user_selected(self, event):
        """Supprime l'utilisateur sélectionné"""
        selection = self.list_box.curselection()
        if not selection:
            return

        index = selection[0]
        username_text = self.list_box.get(index)
        # Enlever l'emoji
        username = username_text.replace("👤 ", "").strip()

        # Confirmation
        response = messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de supprimer l'utilisateur '{username}' ?"
        )

        if response:
            success, message = delete_user(username)
            if success:
                self.status_label.config(text=f"✓ {message}", fg="#4CAF50")
                self.load_users()
            else:
                messagebox.showerror("Erreur", message)
                self.status_label.config(text=f"❌ {message}", fg="#d32f2f")
