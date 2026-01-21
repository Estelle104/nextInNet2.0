import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from backend.config_manager import get_devices

class ListUserView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f5f5")
        self.controller = controller
        
        # Couleurs
        BG_COLOR = "#eaf2fb"
        BTN_COLOR = "#1e88e5"
        TEXT_COLOR = "#0d47a1"

        # Titre
        title = tk.Label(
            self,
            text="Registered Network Devices",
            font=("Arial", 16, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title.pack(pady=15)

        # Frame pour la table
        frame_table = tk.Frame(self, bg=BG_COLOR)
        frame_table.pack(pady=10, padx=20, fill="both", expand=True)

        # En-têtes
        header_frame = tk.Frame(frame_table, bg=TEXT_COLOR)
        header_frame.pack(fill="x", pady=(0, 5))

        tk.Label(header_frame, text="IP Address", font=("Arial", 11, "bold"), 
                fg="white", bg=TEXT_COLOR, width=20).pack(side="left", padx=10)
        tk.Label(header_frame, text="MAC Address", font=("Arial", 11, "bold"), 
                fg="white", bg=TEXT_COLOR, width=25).pack(side="left", padx=10)

        # Listbox pour afficher les devices
        self.list_box = tk.Listbox(frame_table, height=15, font=("Arial", 10))
        self.list_box.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(self.list_box)
        scrollbar.pack(side="right", fill="y")
        self.list_box.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.list_box.yview)

        # Charger les devices
        self.load_devices()

        # Frame pour les boutons
        button_frame = tk.Frame(self, bg="#f5f5f5")
        button_frame.pack(pady=20)

        # Bouton ajouter
        add_button = tk.Button(
            button_frame,
            text="Add New Device",
            bg=BTN_COLOR,
            fg="white",
            font=("Arial", 11, "bold"),
            command=lambda: controller.show_frame("CreateUserView")
        )
        add_button.pack(side="left", padx=10)

        # Bouton rafraîchir
        refresh_button = tk.Button(
            button_frame,
            text="Refresh",
            bg="#4caf50",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.load_devices
        )
        refresh_button.pack(side="left", padx=10)

    def load_devices(self):
        """Affiche les devices enregistrés"""
        self.list_box.delete(0, tk.END)

        devices = get_devices()

        if not devices:
            self.list_box.insert(tk.END, "No devices registered yet")
        else:
            for device in devices:
                ip = device.get('ip', 'N/A')
                mac = device.get('mac', 'N/A')
                text = f"{ip:<20} {mac:<25}"
                self.list_box.insert(tk.END, text)
