import tkinter as tk
from tkinter import ttk, messagebox
import os

# --- Backend import ---
from backend.utils import check_login
import dhcp_server  # ton backend DHCP

BASE = os.path.join(os.path.dirname(__file__), "base.txt")

# --- Fonctions backend simplifiées ---
def load_users():
    """Charge les utilisateurs (MAC -> IP) depuis base.txt"""
    data = {}
    try:
        with open(BASE) as f:
            for l in f:
                parts = l.strip().split("||")
                if len(parts) == 2:
                    m, ip = parts
                    data[m] = ip
    except FileNotFoundError:
        pass
    return data

def add_user(mac, ip):
    """Ajoute un utilisateur dans base.txt"""
    data = load_users()
    data[mac] = ip
    with open(BASE, "w") as f:
        for m, ip in data.items():
            f.write(f"{m}||{ip}\n")

# --- Interface principale ---
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fenêtre principale")
        self.geometry("800x600")
        
        # Notebook (barre d'onglets)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        
        # Onglets
        self.user_tab = ttk.Frame(notebook)
        self.log_tab = ttk.Frame(notebook)
        self.notif_tab = ttk.Frame(notebook)
        
        notebook.add(self.user_tab, text="Gestion User")
        notebook.add(self.log_tab, text="Gestion Log")
        notebook.add(self.notif_tab, text="Notifications")
        
        # Construire chaque onglet
        self.build_user_tab()
        self.build_log_tab()
        self.build_notif_tab()
    
    # --- Onglet Gestion User ---
    def build_user_tab(self):
        frame_buttons = tk.Frame(self.user_tab)
        frame_buttons.pack(pady=10)
        
        btn_add = tk.Button(frame_buttons, text="Ajouter User", command=self.show_add_user)
        btn_add.pack(side="left", padx=10)
        
        btn_list = tk.Button(frame_buttons, text="Liste des Users", command=self.show_list_users)
        btn_list.pack(side="left", padx=10)
        
        self.user_content = tk.Frame(self.user_tab)
        self.user_content.pack(fill="both", expand=True)
    
    def show_add_user(self):
        for widget in self.user_content.winfo_children():
            widget.destroy()
        
        tk.Label(self.user_content, text="Adresse IP:").pack(pady=5)
        entry_ip = tk.Entry(self.user_content)
        entry_ip.pack(pady=5)
        
        tk.Label(self.user_content, text="Adresse MAC:").pack(pady=5)
        entry_mac = tk.Entry(self.user_content)
        entry_mac.pack(pady=5)
        
        def add_action():
            ip = entry_ip.get()
            mac = entry_mac.get()
            if ip and mac:
                add_user(mac, ip)
                messagebox.showinfo("Succès", f"User {mac} ajouté avec IP {ip}")
        
        tk.Button(self.user_content, text="Ajouter", command=add_action).pack(pady=10)
    
    def show_list_users(self):
        for widget in self.user_content.winfo_children():
            widget.destroy()
        
        users = load_users()
        
        tree = ttk.Treeview(self.user_content, columns=("MAC", "IP"), show="headings")
        tree.heading("MAC", text="Adresse MAC")
        tree.heading("IP", text="Adresse IP")
        
        for mac, ip in users.items():
            tree.insert("", "end", values=(mac, ip))
        
        tree.pack(fill="both", expand=True)
    
    # --- Onglet Gestion Log ---
    def build_log_tab(self):
        frame_buttons = tk.Frame(self.log_tab)
        frame_buttons.pack(pady=10)
        
        btn_realtime = tk.Button(frame_buttons, text="Voir log en temps réel", command=self.show_realtime_log)
        btn_realtime.pack(side="left", padx=10)
        
        btn_history = tk.Button(frame_buttons, text="Historique log", command=self.show_history_log)
        btn_history.pack(side="left", padx=10)
        
        self.log_content = tk.Frame(self.log_tab)
        self.log_content.pack(fill="both", expand=True)
    
    def show_realtime_log(self):
        for widget in self.log_content.winfo_children():
            widget.destroy()
        
        tk.Label(self.log_content, text="Logs en temps réel (simulation)").pack()
        logbox = tk.Listbox(self.log_content)
        logbox.pack(fill="both", expand=True)
        
        # Simulation de logs
        logs = ["[INFO] DHCP démarré", "[WARN] IP inconnue détectée", "[INFO] User ajouté"]
        for l in logs:
            logbox.insert("end", l)
    
    def show_history_log(self):
        for widget in self.log_content.winfo_children():
            widget.destroy()
        
        tk.Label(self.log_content, text="Historique des logs (simulation)").pack()
        tree = ttk.Treeview(self.log_content, columns=("Date", "IP", "Message"), show="headings")
        tree.heading("Date", text="Date")
        tree.heading("IP", text="IP")
        tree.heading("Message", text="Message")
        
        # Simulation
        history = [
            ("2026-01-17", "192.168.1.10", "Connexion réussie"),
            ("2026-01-17", "192.168.1.20", "IP inconnue"),
        ]
        for h in history:
            tree.insert("", "end", values=h)
        
        tree.pack(fill="both", expand=True)
    
    # --- Onglet Notifications ---
    def build_notif_tab(self):
        tk.Label(self.notif_tab, text="Liste des malfaiteurs (IP inconnues)").pack(pady=10)
        
        tree = ttk.Treeview(self.notif_tab, columns=("IP", "Détail"), show="headings")
        tree.heading("IP", text="IP")
        tree.heading("Détail", text="Détail")
        
        # Simulation
        malfaiteurs = [
            ("192.168.1.99", "Tentative non autorisée"),
            ("192.168.1.55", "MAC inconnue"),
        ]
        for m in malfaiteurs:
            tree.insert("", "end", values=m)
        
        tree.pack(fill="both", expand=True)

# --- Lancer l'app ---
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
