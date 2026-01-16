import tkinter as tk
from tkinter import messagebox
from assets.theme import *

class LoginView(tk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, bg=BG)
        self.on_success = on_success
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Connexion",
                 font=("Arial", 20, "bold"),
                 bg=BG, fg=TEXT).pack(pady=30)

        self.user = tk.Entry(self, width=30)
        self.user.pack(pady=10)
        self.user.insert(0, "Nom d'utilisateur")

        self.pwd = tk.Entry(self, width=30, show="*")
        self.pwd.pack(pady=10)
        self.pwd.insert(0, "Mot de passe")

        tk.Button(self, text="Se connecter",
                  bg=PRIMARY, fg="white",
                  relief="flat",
                  padx=20, pady=10,
                  command=self.login).pack(pady=20)

    def login(self):
        if self.user.get() == "admin" and self.pwd.get() == "admin":
            self.on_success()
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects")
