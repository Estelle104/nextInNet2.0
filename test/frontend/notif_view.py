import tkinter as tk
from assets.theme import *

class NotifView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Notifications",
                 font=("Arial", 16), bg=BG).pack(pady=10)

        self.list = tk.Listbox(self)
        self.list.pack(fill="both", expand=True)

        self.list.insert("end", "[HAUTE] IP inconnue 192.168.12.200")
        self.list.insert("end", "[MOYENNE] Tentative répétée 192.168.12.55")
