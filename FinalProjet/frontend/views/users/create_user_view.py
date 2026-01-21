import tkinter as tk
from tkinter import messagebox
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from backend.config_manager import add_device

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
            text="Register Network Device",
            font=("Arial", 18, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title.pack(pady=20)

        # IP Address
        tk.Label(
            self,
            text="IP Address",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 11)
        ).pack()

        self.ip_entry = tk.Entry(self, width=30)
        self.ip_entry.pack(pady=5)
        self.ip_entry.insert(0, "192.168.1.")

        # MAC Address
        tk.Label(
            self,
            text="MAC Address",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 11)
        ).pack()

        self.mac_entry = tk.Entry(self, width=30)
        self.mac_entry.pack(pady=5)
        self.mac_entry.insert(0, "AA:BB:CC:DD:EE:FF")

        # Bouton ajouter
        add_button = tk.Button(
            self,
            text="Add Device",
            bg=BTN_COLOR,
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.add_device
        )
        add_button.pack(pady=20)

        # Navigation button back to ListUserView
        if controller:
            nav_button = tk.Button(
                self,
                text="Go to Device List",
                bg=BTN_COLOR,
                fg="white",
                font=("Arial", 11, "bold"),
                command=lambda: controller.show_frame("ListUserView")
            )
            nav_button.pack(pady=10)

    def add_device(self):
        ip = self.ip_entry.get().strip()
        mac = self.mac_entry.get().strip()
        
        # Validation
        if not ip or ip == "192.168.1.":
            messagebox.showerror("Error", "Please enter a valid IP address")
            return
        
        if not mac or mac == "AA:BB:CC:DD:EE:FF":
            messagebox.showerror("Error", "Please enter a valid MAC address")
            return
        
        # Valider format IP basique
        try:
            parts = ip.split('.')
            if len(parts) != 4 or not all(0 <= int(p) <= 255 for p in parts):
                raise ValueError("Invalid IP format")
        except ValueError:
            messagebox.showerror("Error", "Invalid IP address format (e.g., 192.168.1.100)")
            return
        
        # Valider format MAC
        mac_parts = mac.split(':')
        if len(mac_parts) != 6:
            messagebox.showerror("Error", "Invalid MAC format (e.g., AA:BB:CC:DD:EE:FF)")
            return
        
        # Ajouter le device (MAC, IP)
        if add_device(mac, ip):
            messagebox.showinfo("Success", f"Device added:\nIP: {ip}\nMAC: {mac}")
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, "192.168.1.")
            self.mac_entry.delete(0, tk.END)
            self.mac_entry.insert(0, "AA:BB:CC:DD:EE:FF")
            
            # Retour à la liste
            if self.controller:
                self.controller.show_frame("ListUserView")
        else:
            messagebox.showerror("Error", "Failed to add device")
