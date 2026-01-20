import tkinter as tk
from tkinter import ttk

# Exemple : ta fonction qui retourne les notifications en temps réel
def get_notifications():
    # Ici tu mets ton vrai code (lecture DB, logs, API, etc.)
    # Pour l'exemple, je simule une liste qui peut changer
    return [
        {"niveau": "HIGH", "date": "2026-01-16 14:35:22", "ip": "192.168.1.99", "mac": "00:1B:44:XX:XX:XX", "tentatives": 5},
        {"niveau": "MEDIUM", "date": "2026-01-16 13:20:15", "ip": "192.168.1.87", "mac": "00:1B:44:YY:YY:YY", "tentatives": 3},
        {"niveau": "LOW", "date": "2026-01-16 12:10:08", "ip": "192.168.1.123", "mac": "00:1B:44:ZZ:ZZ:ZZ", "tentatives": 1},
    ]

def afficher_details(index):
    notif = notifications[index]
    details_var.set(
        f"Niveau: {notif['niveau']}\n"
        f"Date: {notif['date']}\n"
        f"IP: {notif['ip']}\n"
        f"MAC: {notif['mac']}\n"
        f"Tentatives: {notif['tentatives']}"
    )

def update_notifications():
    global notifications
    notifications = get_notifications()  # récupère les nouvelles données
    notif_listbox.delete(0, tk.END)      # vide la liste
    for notif in notifications:
        notif_listbox.insert(tk.END, f"{notif['niveau']} - {notif['ip']}")
    # relancer la mise à jour dans 5 secondes
    root.after(5000, update_notifications)

# Fenêtre principale
root = tk.Tk()
root.title("Application de Surveillance")
root.geometry("800x400")

# Barre de navigation
nav_frame = tk.Frame(root, bg="#2c3e50", height=50)
nav_frame.pack(fill="x")
for label in ["Gestion User", "Gestion Log", "Notifications"]:
    btn = tk.Button(nav_frame, text=label, bg="#34495e", fg="white", padx=20)
    btn.pack(side="left", padx=5, pady=10)

# Panneau principal
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Liste des notifications
notif_frame = tk.Frame(main_frame, width=300, bg="#ecf0f1")
notif_frame.pack(side="left", fill="y")
tk.Label(notif_frame, text="Notifications de sécurité", bg="#ecf0f1", font=("Arial", 12, "bold")).pack(pady=10)

notif_listbox = tk.Listbox(notif_frame, font=("Arial", 10))
notif_listbox.pack(fill="both", expand=True, padx=10, pady=5)
notif_listbox.bind("<<ListboxSelect>>", lambda e: afficher_details(notif_listbox.curselection()[0]))

# Détails
details_frame = tk.Frame(main_frame, bg="#bdc3c7")
details_frame.pack(side="right", fill="both", expand=True)
tk.Label(details_frame, text="Détails de la notification", bg="#bdc3c7", font=("Arial", 12, "bold")).pack(pady=10)

details_var = tk.StringVar()
details_label = tk.Label(details_frame, textvariable=details_var, bg="#bdc3c7", font=("Arial", 10), justify="left")
details_label.pack(padx=20, pady=10)

# Lancer la mise à jour automatique
notifications = []
update_notifications()

root.mainloop()
