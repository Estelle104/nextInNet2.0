#!/usr/bin/env python3
"""
Vue Notifications - Affiche les alertes de sécurité
Affiche les machines inconnues, tentatives d'accès, blocages, etc.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import os
from datetime import datetime

NOTIFICATIONS_FILE = "/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0/FinalProjet/backend/logs/notifications.log"

class NotificationsView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.auto_refresh = tk.BooleanVar(value=True)
        self.notification_filter = tk.StringVar(value="ALL")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface de la vue notifications"""
        
        # En-tête avec options
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        # Filtre par type
        ttk.Label(header_frame, text="Filtre:").pack(side="left", padx=5)
        filter_combo = ttk.Combobox(
            header_frame, 
            textvariable=self.notification_filter,
            values=["ALL", "WARNING", "BLOCKED", "TIMEOUT", "INFO"],
            state="readonly",
            width=15
        )
        filter_combo.pack(side="left", padx=5)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_notifications())
        
        # Checkbox auto-refresh
        ttk.Checkbutton(
            header_frame,
            text="Auto-refresh (2s)",
            variable=self.auto_refresh,
            command=self.toggle_auto_refresh
        ).pack(side="left", padx=20)
        
        # Bouton refresh manuel
        ttk.Button(header_frame, text="Rafraîchir", command=self.refresh_notifications).pack(side="left", padx=5)
        
        # Bouton clear
        ttk.Button(header_frame, text="Effacer", command=self.clear_notifications).pack(side="left", padx=5)
        
        # Display des notifications
        display_frame = ttk.Frame(self)
        display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar + Text widget
        scrollbar = ttk.Scrollbar(display_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.notif_display = scrolledtext.ScrolledText(
            display_frame,
            height=20,
            width=80,
            bg="#1E1E1E",
            fg="#FFFFFF",
            font=("Courier", 9),
            yscrollcommand=scrollbar.set
        )
        self.notif_display.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.notif_display.yview)
        
        # Configurer les couleurs
        self.setup_colors()
        
        # Barre de statut
        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", padx=10, pady=5)
        self.status_label = ttk.Label(status_frame, text="En attente...", relief="sunken")
        self.status_label.pack(fill="x")
        
        # Premier chargement
        self.refresh_notifications()
        
        # Auto-refresh
        if self.auto_refresh.get():
            self.start_auto_refresh()
    
    def setup_colors(self):
        """Configure les couleurs pour les différents types d'alerte"""
        self.notif_display.tag_config("warning", foreground="#FFB74D", font=("Courier", 9, "bold"))    # Orange
        self.notif_display.tag_config("blocked", foreground="#EF5350", font=("Courier", 9, "bold"))    # Rouge
        self.notif_display.tag_config("timeout", foreground="#BA68C8", font=("Courier", 9, "bold"))    # Violet
        self.notif_display.tag_config("info", foreground="#64B5F6", font=("Courier", 9))                # Bleu
        self.notif_display.tag_config("timestamp", foreground="#81C784", font=("Courier", 8))          # Vert clair
    
    def get_notifications(self):
        """Récupère les notifications du fichier"""
        notifications = []
        try:
            if not os.path.exists(NOTIFICATIONS_FILE):
                return notifications
            
            with open(NOTIFICATIONS_FILE, 'r') as f:
                notifications = f.readlines()
            
            # Appliquer le filtre
            filter_type = self.notification_filter.get()
            if filter_type != "ALL":
                notifications = [n for n in notifications if f"[{filter_type}]" in n]
            
            return notifications
        except Exception as e:
            return [f"[ERROR] {str(e)}\n"]
    
    def refresh_notifications(self):
        """Rafraîchit l'affichage des notifications"""
        notifications = self.get_notifications()
        
        self.notif_display.config(state="normal")
        self.notif_display.delete("1.0", "end")
        
        if not notifications:
            self.notif_display.insert("end", "[INFO] Aucune notification\n")
            self.status_label.config(text="✓ Aucune alerte")
            return
        
        # Compter par type
        warning_count = sum(1 for n in notifications if "[WARNING]" in n)
        blocked_count = sum(1 for n in notifications if "[BLOCKED]" in n)
        timeout_count = sum(1 for n in notifications if "[TIMEOUT]" in n)
        
        # Afficher le résumé
        summary = f"⚠️  {warning_count} avertissement(s) | 🚫 {blocked_count} bloqué(s) | ⏱️ {timeout_count} timeout(s)\n"
        summary += "=" * 80 + "\n\n"
        self.notif_display.insert("end", summary, "info")
        
        # Afficher les notifications (les plus récentes en dernier)
        for notif in notifications:
            if "[WARNING]" in notif:
                self.notif_display.insert("end", notif, "warning")
            elif "[BLOCKED]" in notif:
                self.notif_display.insert("end", notif, "blocked")
            elif "[TIMEOUT]" in notif:
                self.notif_display.insert("end", notif, "timeout")
            else:
                self.notif_display.insert("end", notif, "info")
        
        # Scroll vers le bas
        self.notif_display.see("end")
        self.notif_display.config(state="disabled")
        
        # Mettre à jour le statut
        self.status_label.config(text=f"✓ {len(notifications)} notification(s) | Dernière: {datetime.now().strftime('%H:%M:%S')}")
    
    def toggle_auto_refresh(self):
        """Bascule l'auto-refresh"""
        if self.auto_refresh.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """Démarre l'auto-refresh toutes les 2 secondes"""
        def auto_refresh_loop():
            while self.auto_refresh.get():
                try:
                    self.refresh_notifications()
                    threading.Event().wait(2)  # Attend 2 secondes
                except:
                    pass
        
        refresh_thread = threading.Thread(target=auto_refresh_loop, daemon=True)
        refresh_thread.start()
    
    def stop_auto_refresh(self):
        """Arrête l'auto-refresh"""
        self.auto_refresh.set(False)
    
    def clear_notifications(self):
        """Efface le fichier de notifications"""
        try:
            if os.path.exists(NOTIFICATIONS_FILE):
                open(NOTIFICATIONS_FILE, 'w').close()
            self.refresh_notifications()
            self.status_label.config(text="✓ Notifications effacées")
        except Exception as e:
            self.status_label.config(text=f"✗ Erreur: {str(e)}")
