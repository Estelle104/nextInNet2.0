import tkinter as tk
from tkinter import ttk

# Palette de couleurs bleues modernes
COLORS = {
    'primary': '#1e3a8a',      # Bleu foncé
    'secondary': '#3b82f6',    # Bleu vif
    'accent': '#60a5fa',       # Bleu clair
    'bg_dark': '#0f172a',      # Bleu très foncé
    'bg_light': '#e0f2fe',     # Bleu très clair
    'text_light': '#f1f5f9',   # Texte clair
    'text_dark': '#0f172a',    # Texte foncé
    'high': '#ef4444',         # Rouge pour HIGH
    'medium': '#f59e0b',       # Orange pour MEDIUM
    'low': '#10b981',          # Vert pour LOW
}

def get_notifications():
    return [
        {"niveau": "HIGH", "date": "2026-01-16 14:35:22", "ip": "192.168.1.99", "mac": "00:1B:44:XX:XX:XX", "tentatives": 5},
        {"niveau": "MEDIUM", "date": "2026-01-16 13:20:15", "ip": "192.168.1.87", "mac": "00:1B:44:YY:YY:YY", "tentatives": 3},
        {"niveau": "LOW", "date": "2026-01-16 12:10:08", "ip": "192.168.1.123", "mac": "00:1B:44:ZZ:ZZ:ZZ", "tentatives": 1},
    ]

def afficher_details(event=None):
    selection = notif_listbox.curselection()
    if selection:
        index = selection[0]
        notif = notifications[index]
        
        # Effacer les anciens widgets
        for widget in details_content_frame.winfo_children():
            widget.destroy()
        
        # Titre avec niveau coloré
        niveau_color = COLORS.get(notif['niveau'].lower(), COLORS['secondary'])
        tk.Label(
            details_content_frame, 
            text=f"🔔 Alerte {notif['niveau']}", 
            bg=COLORS['bg_light'],
            fg=niveau_color,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(0, 20))
        
        # Informations détaillées
        details = [
            ("📅 Date", notif['date']),
            ("🌐 Adresse IP", notif['ip']),
            ("💻 Adresse MAC", notif['mac']),
            ("⚠️ Tentatives", str(notif['tentatives']))
        ]
        
        for label, value in details:
            frame = tk.Frame(details_content_frame, bg=COLORS['bg_light'])
            frame.pack(fill="x", pady=8, padx=20)
            
            tk.Label(
                frame, 
                text=label, 
                bg=COLORS['bg_light'],
                fg=COLORS['primary'],
                font=("Segoe UI", 11, "bold"),
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                frame, 
                text=value, 
                bg=COLORS['bg_light'],
                fg=COLORS['text_dark'],
                font=("Segoe UI", 11),
                anchor="e"
            ).pack(side="right")
        
        # Bouton d'action
        action_btn = tk.Button(
            details_content_frame,
            text="📊 Voir les détails complets",
            bg=COLORS['secondary'],
            fg=COLORS['text_light'],
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10
        )
        action_btn.pack(pady=20)

def update_notifications():
    global notifications
    notifications = get_notifications()
    notif_listbox.delete(0, tk.END)
    
    for notif in notifications:
        notif_listbox.insert(tk.END, f"  {notif['niveau']} - {notif['ip']}")
        
        # Colorier selon le niveau
        idx = notif_listbox.size() - 1
        color = COLORS.get(notif['niveau'].lower(), COLORS['secondary'])
        notif_listbox.itemconfig(idx, {'fg': color})
    
    root.after(5000, update_notifications)

# Fenêtre principale
root = tk.Tk()
root.title("🛡️ Système de Surveillance Réseau")
root.geometry("1000x600")
root.configure(bg=COLORS['bg_dark'])

# Barre de navigation avec dégradé bleu
nav_frame = tk.Frame(root, bg=COLORS['primary'], height=60)
nav_frame.pack(fill="x")
nav_frame.pack_propagate(False)

# Logo/Titre
logo_label = tk.Label(
    nav_frame, 
    text="🛡️ SecureNet",
    bg=COLORS['primary'],
    fg=COLORS['text_light'],
    font=("Segoe UI", 16, "bold")
)
logo_label.pack(side="left", padx=20, pady=15)

# Boutons de navigation
nav_buttons = ["👥 Gestion User", "📋 Gestion Log", "🔔 Notifications"]
for label in nav_buttons:
    btn = tk.Button(
        nav_frame, 
        text=label,
        bg=COLORS['secondary'],
        fg=COLORS['text_light'],
        font=("Segoe UI", 10, "bold"),
        relief=tk.FLAT,
        padx=20,
        pady=8,
        cursor="hand2",
        activebackground=COLORS['accent'],
        activeforeground=COLORS['text_light']
    )
    btn.pack(side="left", padx=5, pady=15)

# Panneau principal
main_frame = tk.Frame(root, bg=COLORS['bg_dark'])
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# ===== PANNEAU GAUCHE : Liste des notifications =====
notif_frame = tk.Frame(main_frame, bg=COLORS['bg_light'], relief=tk.RAISED, bd=2)
notif_frame.pack(side="left", fill="both", padx=(0, 5), pady=0, expand=False)
notif_frame.configure(width=400)

# En-tête
header_frame = tk.Frame(notif_frame, bg=COLORS['secondary'], height=50)
header_frame.pack(fill="x")
header_frame.pack_propagate(False)

tk.Label(
    header_frame, 
    text="🔔 Notifications de sécurité",
    bg=COLORS['secondary'],
    fg=COLORS['text_light'],
    font=("Segoe UI", 13, "bold")
).pack(pady=12)

# Compteur de notifications
count_frame = tk.Frame(notif_frame, bg=COLORS['bg_light'])
count_frame.pack(fill="x", pady=10, padx=15)

count_label = tk.Label(
    count_frame,
    text="Total: 3 alertes",
    bg=COLORS['bg_light'],
    fg=COLORS['primary'],
    font=("Segoe UI", 10, "bold")
)
count_label.pack(side="left")

# Listbox avec scrollbar
listbox_frame = tk.Frame(notif_frame, bg=COLORS['bg_light'])
listbox_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

scrollbar = tk.Scrollbar(listbox_frame)
scrollbar.pack(side="right", fill="y")

notif_listbox = tk.Listbox(
    listbox_frame,
    font=("Consolas", 11),
    bg="white",
    fg=COLORS['text_dark'],
    selectbackground=COLORS['accent'],
    selectforeground=COLORS['text_light'],
    relief=tk.FLAT,
    borderwidth=0,
    highlightthickness=1,
    highlightcolor=COLORS['secondary'],
    highlightbackground=COLORS['accent'],
    yscrollcommand=scrollbar.set
)
notif_listbox.pack(side="left", fill="both", expand=True)
scrollbar.config(command=notif_listbox.yview)

notif_listbox.bind("<<ListboxSelect>>", afficher_details)

# ===== PANNEAU DROIT : Détails =====
details_frame = tk.Frame(main_frame, bg=COLORS['bg_light'], relief=tk.RAISED, bd=2)
details_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

# En-tête détails
details_header = tk.Frame(details_frame, bg=COLORS['secondary'], height=50)
details_header.pack(fill="x")
details_header.pack_propagate(False)

tk.Label(
    details_header, 
    text="📊 Détails de la notification",
    bg=COLORS['secondary'],
    fg=COLORS['text_light'],
    font=("Segoe UI", 13, "bold")
).pack(pady=12)

# Contenu des détails avec scrollbar
details_canvas_frame = tk.Frame(details_frame, bg=COLORS['bg_light'])
details_canvas_frame.pack(fill="both", expand=True)

details_content_frame = tk.Frame(details_canvas_frame, bg=COLORS['bg_light'])
details_content_frame.pack(fill="both", expand=True, pady=20)

# Message par défaut
default_msg = tk.Label(
    details_content_frame,
    text="👈 Sélectionnez une notification\npour voir les détails",
    bg=COLORS['bg_light'],
    fg=COLORS['primary'],
    font=("Segoe UI", 12),
    justify="center"
)
default_msg.pack(expand=True)

# Lancer la mise à jour automatique
notifications = []
update_notifications()

root.mainloop()