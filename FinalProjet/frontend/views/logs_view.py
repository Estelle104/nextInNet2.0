import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "assets"))
from theme import *
import subprocess
import tkinter as tk
import threading
import time
from datetime import datetime

class LogsView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self.pack(fill="both", expand=True)
        
        # Variables
        self.current_log_type = "realtime"
        self.auto_refresh_enabled = True
        self.refresh_interval = 2000  # 2 secondes en millisecondes
        self.refresh_job = None
        self.last_logs = []

        # Title
        title_frame = tk.Frame(self, bg=BG)
        title_frame.pack(fill="x", pady=10, padx=10)
        
        tk.Label(title_frame, text="📊 Logs en Temps Réel", font=("Arial", 16, "bold"), bg=BG, fg=PRIMARY).pack(side="left")
        
        # Auto-refresh toggle
        self.auto_refresh_var = tk.BooleanVar(value=True)
        tk.Checkbutton(title_frame, text="🔄 Auto-refresh (2s)", variable=self.auto_refresh_var, 
                      bg=BG, fg=TEXT, font=("Arial", 10), command=self.toggle_auto_refresh).pack(side="right", padx=5)

        # Tab buttons frame
        self.tab_frame = tk.Frame(self, bg=BG, highlightthickness=1, highlightbackground=SECONDARY)
        self.tab_frame.pack(fill="x", pady=10, padx=10)

        self.realtime_button = tk.Button(self.tab_frame, text="⚡ Temps Réel", bg=PRIMARY, fg="white", 
                                         font=("Arial", 10, "bold"), command=self.show_realtime_logs, relief="raised")
        self.realtime_button.pack(side="left", padx=5, pady=5)

        self.history_button = tk.Button(self.tab_frame, text="📚 Historique", bg=SECONDARY, fg="white",
                                       font=("Arial", 10), command=self.show_history_logs)
        self.history_button.pack(side="left", padx=5, pady=5)

        # Refresh button
        self.refresh_button = tk.Button(self.tab_frame, text="🔄 Rafraîchir", bg="#4CAF50", fg="white",
                                       font=("Arial", 10), command=self.manual_refresh)
        self.refresh_button.pack(side="left", padx=5, pady=5)
        
        # Clear button
        self.clear_button = tk.Button(self.tab_frame, text="🗑️ Effacer", bg="#FF9800", fg="white",
                                     font=("Arial", 10), command=self.clear_logs)
        self.clear_button.pack(side="left", padx=5, pady=5)

        # Log display area with scrollbar
        display_frame = tk.Frame(self, bg=BG)
        display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(display_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.log_display = tk.Text(display_frame, height=20, bg="#1e1e1e", fg="#d4d4d4", 
                                   wrap="word", font=("Courier", 9), yscrollcommand=scrollbar.set)
        self.log_display.pack(fill="both", expand=True)
        scrollbar.config(command=self.log_display.yview)
        self.log_display.config(state="disabled")

        # Configurer les tags de couleur
        self.setup_colors()

        # Status bar
        self.status_bar = tk.Label(self, text="⏳ Initialisation...", font=("Arial", 9), bg=SECONDARY, fg="white")
        self.status_bar.pack(fill="x", padx=10, pady=5, side="bottom")

        # Show real-time logs by default
        self.show_realtime_logs()

    def setup_colors(self):
        """Configure les couleurs pour les différents types de logs"""
        self.log_display.tag_config("connection", foreground="#4CAF50", font=("Courier", 9, "bold"))  # Vert
        self.log_display.tag_config("success", foreground="#81C784", font=("Courier", 9, "bold"))     # Vert clair
        self.log_display.tag_config("error", foreground="#EF5350", font=("Courier", 9, "bold"))       # Rouge
        self.log_display.tag_config("warning", foreground="#FFB74D", font=("Courier", 9))             # Orange
        self.log_display.tag_config("info", foreground="#64B5F6", font=("Courier", 9))                # Bleu
        self.log_display.tag_config("test", foreground="#BA68C8", font=("Courier", 9))                # Violet
        self.log_display.tag_config("server", foreground="#FFD54F", font=("Courier", 9))              # Jaune
        self.log_display.tag_config("normal", foreground="#d4d4d4", font=("Courier", 9))              # Gris

    def toggle_auto_refresh(self):
        """Bascule l'auto-refresh"""
        self.auto_refresh_enabled = self.auto_refresh_var.get()
        if self.auto_refresh_enabled and self.current_log_type == "realtime":
            self.schedule_next_refresh()
        elif self.refresh_job:
            self.after_cancel(self.refresh_job)
            self.refresh_job = None

    def show_realtime_logs(self):
        """Affiche les logs en temps réel"""
        self.current_log_type = "realtime"
        self.auto_refresh_enabled = self.auto_refresh_var.get()
        self.update_tab_colors(self.realtime_button, self.history_button)
        self.status_bar.config(text="⏳ Chargement des logs en temps réel...")
        self.after(100, self._fetch_realtime_async)

    def show_history_logs(self):
        """Affiche l'historique des logs"""
        self.current_log_type = "history"
        self.auto_refresh_enabled = False  # Pas d'auto-refresh pour l'historique
        self.update_tab_colors(self.history_button, self.realtime_button)
        self.status_bar.config(text="⏳ Chargement de l'historique...")
        if self.refresh_job:
            self.after_cancel(self.refresh_job)
            self.refresh_job = None
        self.after(100, self._fetch_history_async)

    def _fetch_realtime_async(self):
        """Récupère les logs en temps réel de manière asynchrone"""
        threading.Thread(target=self._fetch_and_display, args=("realtime",), daemon=True).start()

    def _fetch_history_async(self):
        """Récupère l'historique de manière asynchrone"""
        threading.Thread(target=self._fetch_and_display, args=("history",), daemon=True).start()

    def _fetch_and_display(self, log_type):
        """Thread pour récupérer et afficher les logs"""
        logs = self.fetch_logs(log_type)
        self.after(0, lambda: self.display_logs(logs, log_type))
        
        # Programmer le prochain rafraîchissement si auto-refresh actif
        if self.auto_refresh_enabled and log_type == "realtime":
            self.schedule_next_refresh()

    def schedule_next_refresh(self):
        """Programme le prochain rafraîchissement automatique"""
        if self.refresh_job:
            self.after_cancel(self.refresh_job)
        self.refresh_job = self.after(self.refresh_interval, self._fetch_realtime_async)

    def manual_refresh(self):
        """Rafraîchit manuellement"""
        if self.current_log_type == "realtime":
            self.show_realtime_logs()
        else:
            self.show_history_logs()

    def clear_logs(self):
        """Efface l'affichage des logs"""
        self.log_display.config(state="normal")
        self.log_display.delete("1.0", "end")
        self.log_display.config(state="disabled")
        self.status_bar.config(text="✓ Affichage effacé")

    def update_tab_colors(self, active_button, inactive_button):
        """Met à jour les couleurs des onglets"""
        active_button.config(bg=PRIMARY, relief="sunken", font=("Arial", 10, "bold"))
        inactive_button.config(bg=SECONDARY, relief="raised", font=("Arial", 10))

    def fetch_logs(self, log_type):
        """Récupère les logs depuis les fichiers"""
        try:
            # Chemins des fichiers de logs
            logs_dir = os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "backend",
                "logs"
            )
            
            # Chercher les fichiers de logs disponibles
            all_logs = []
            
            # Ajouter les logs TCP (Connexion.log) - Principal
            connection_log_file = os.path.join(logs_dir, "Connexion.log")
            if os.path.exists(connection_log_file):
                try:
                    with open(connection_log_file, 'r') as f:
                        all_logs.extend(f.readlines())
                except:
                    pass
            
            # Ajouter les logs DHCP (dhcp.log) - Secondaire
            dhcp_log_file = os.path.join(logs_dir, "dhcp.log")
            if os.path.exists(dhcp_log_file):
                try:
                    with open(dhcp_log_file, 'r') as f:
                        all_logs.extend(f.readlines())
                except:
                    pass
            
            if not all_logs:
                return ["[INFO] Aucun log disponible\n"]
            
            # Trier les logs par timestamp
            all_logs = sorted(set([line.strip() for line in all_logs if line.strip()]))
            
            # Retourner les logs
            if log_type == "realtime":
                # Les 20 derniers logs
                return all_logs[-20:] if len(all_logs) > 20 else all_logs
            else:  # history
                # Tous les logs
                return all_logs
                    
        except Exception as e:
            return [f"[ERROR] {str(e)}"]

    def get_tag_for_log(self, log_line):
        """Détermine la couleur basée sur le contenu du log"""
        log_upper = log_line.upper()
        
        if "[SUCCESS]" in log_upper or "STARTED" in log_upper or "✓" in log_line:
            return "success"
        elif "[ERROR]" in log_upper or "FAILED" in log_upper or "✗" in log_line:
            return "error"
        elif "[WARNING]" in log_upper or "⚠️" in log_line:
            return "warning"
        elif "[INFO]" in log_upper:
            return "info"
        elif "[TEST]" in log_upper:
            return "test"
        elif "[SERVER]" in log_upper or "[REQUEST]" in log_upper:
            return "server"
        elif "[CONNECTION]" in log_upper or "[REMOTE CONNECTION]" in log_upper:
            return "connection"
        else:
            return "normal"

    def display_logs(self, logs, log_type="realtime"):
        """Affiche les logs avec couleurs"""
        self.log_display.config(state="normal")
        self.log_display.delete("1.0", "end")
        
        if not logs:
            self.log_display.insert("end", "[INFO] En attente de connexions...\n", "info")
        else:
            # Afficher tous les logs
            for log in logs:
                tag = self.get_tag_for_log(log)
                self.log_display.insert("end", log + "\n", tag)

        self.log_display.config(state="disabled")
        
        # Scroll vers le bas
        self.log_display.see("end")
        
        # Mettre à jour la barre de statut
        status_text = f"📊 {len(logs)} log(s) | Mode: {'Temps réel 🔄' if log_type == 'realtime' else 'Historique 📚'}"
        
        if self.auto_refresh_enabled and log_type == "realtime":
            status_text += f" | Auto-refresh: ON (2s)"
        
        self.status_bar.config(text=status_text)
        self.last_logs = logs
