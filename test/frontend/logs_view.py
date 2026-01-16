import tkinter as tk
from assets.theme import *

class LogsView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Logs réseau",
                 font=("Arial", 16), bg=BG).pack(pady=10)

        self.logs = tk.Text(self, height=20)
        self.logs.pack(fill="both", expand=True)

        self.logs.insert("end", "2026-01-16 | 192.168.12.10 | Connexion OK\n")
