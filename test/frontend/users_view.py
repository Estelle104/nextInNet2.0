import tkinter as tk
from assets.theme import *

class UsersView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Gestion des utilisateurs",
                 font=("Arial", 16), bg=BG).pack(pady=10)

        self.ip = tk.Entry(self)
        self.ip.insert(0, "IP")
        self.ip.pack(pady=5)

        self.mac = tk.Entry(self)
        self.mac.insert(0, "MAC")
        self.mac.pack(pady=5)

        tk.Button(self, text="Ajouter",
                  bg=PRIMARY, fg="white").pack(pady=10)

        self.table = tk.Listbox(self, width=60)
        self.table.pack(pady=10)
