import sys
import os
import tkinter as tk
from datetime import datetime

# Thème
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "assets"))
from theme import *

class LogsView(tk.Frame):
    """
    Vue Logs – SAFE Tkinter
    - Aucun thread
    - after() uniquement
    - Annulation propre à la destruction
    """

    def __init__(self, master):
        super().__init__(master, bg=BG)

        # État
        self.current_log_type = "realtime"
        self.auto_refresh_enabled = True
        self.refresh_interval = 16000  # 16s
        self.refresh_job = None
        self.last_logs = []

        self._build_ui()
        self.after(200, self.show_realtime_logs)

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _build_ui(self):
        title = tk.Frame(self, bg=BG)
        title.pack(fill="x", padx=10, pady=10)

        tk.Label(
            title,
            text="📊 Logs du Système",
            font=("Arial", 16, "bold"),
            bg=BG,
            fg=PRIMARY
        ).pack(side="left")

        self.auto_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            title,
            text="🔄 Auto-refresh (16s)",
            variable=self.auto_var,
            bg=BG,
            fg=TEXT,
            command=self.toggle_auto_refresh
        ).pack(side="right")

        tabs = tk.Frame(self, bg=BG)
        tabs.pack(fill="x", padx=10)

        self.btn_realtime = tk.Button(
            tabs, text="⚡ Temps réel",
            bg=PRIMARY, fg="white",
            command=self.show_realtime_logs
        )
        self.btn_realtime.pack(side="left", padx=5)

        self.btn_history = tk.Button(
            tabs, text="📚 Historique",
            bg=SECONDARY, fg="white",
            command=self.show_history_logs
        )
        self.btn_history.pack(side="left", padx=5)

        tk.Button(
            tabs, text="🔄 Rafraîchir",
            bg="#4CAF50", fg="white",
            command=self.manual_refresh
        ).pack(side="left", padx=5)

        tk.Button(
            tabs, text="🗑️ Effacer",
            bg="#FF9800", fg="white",
            command=self.clear_logs
        ).pack(side="left", padx=5)

        display = tk.Frame(self, bg=BG)
        display.pack(fill="both", expand=True, padx=10, pady=10)

        scroll = tk.Scrollbar(display)
        scroll.pack(side="right", fill="y")

        self.text = tk.Text(
            display,
            bg="#1e1e1e",
            fg="#d4d4d4",
            font=("Courier", 9),
            wrap="word",
            yscrollcommand=scroll.set
        )
        self.text.pack(fill="both", expand=True)
        scroll.config(command=self.text.yview)

        self.text.config(state="disabled")
        self._setup_tags()

        self.status = tk.Label(
            self,
            text="⏳ Initialisation…",
            bg=SECONDARY,
            fg="white",
            font=("Arial", 9)
        )
        self.status.pack(fill="x")

    def _setup_tags(self):
        self.text.tag_config("success", foreground="#81C784")
        self.text.tag_config("error", foreground="#EF5350")
        self.text.tag_config("warning", foreground="#FFB74D")
        self.text.tag_config("info", foreground="#64B5F6")
        self.text.tag_config("connection", foreground="#4CAF50", font=("Courier", 9, "bold"))
        self.text.tag_config("normal", foreground="#d4d4d4")

    # --------------------------------------------------
    # Actions
    # --------------------------------------------------
    def toggle_auto_refresh(self):
        self.auto_refresh_enabled = self.auto_var.get()
        if self.auto_refresh_enabled and self.current_log_type == "realtime":
            self._schedule_refresh()
        else:
            self._cancel_refresh()

    def show_realtime_logs(self):
        self.current_log_type = "realtime"
        self.auto_refresh_enabled = self.auto_var.get()
        self._update_tabs(self.btn_realtime, self.btn_history)
        self._load_logs()

    def show_history_logs(self):
        self.current_log_type = "history"
        self.auto_refresh_enabled = False
        self._update_tabs(self.btn_history, self.btn_realtime)
        self._cancel_refresh()
        self._load_logs()

    def manual_refresh(self):
        self._load_logs()

    def clear_logs(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")
        self.status.config(text="✓ Affichage effacé")

    # --------------------------------------------------
    # Logique
    # --------------------------------------------------
    def _update_tabs(self, active, inactive):
        active.config(relief="sunken", bg=PRIMARY)
        inactive.config(relief="raised", bg=SECONDARY)

    def _schedule_refresh(self):
        self._cancel_refresh()
        self.refresh_job = self.after(self.refresh_interval, self._load_logs)

    def _cancel_refresh(self):
        if self.refresh_job:
            try:
                self.after_cancel(self.refresh_job)
            except Exception:
                pass
            self.refresh_job = None

    def _load_logs(self):
        logs = self._fetch_logs(self.current_log_type)
        self._display_logs(logs)

        if self.auto_refresh_enabled and self.current_log_type == "realtime":
            self._schedule_refresh()

    def _fetch_logs(self, mode):
        logs_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "backend", "logs")
        )

        if not os.path.exists(logs_dir):
            return ["[INFO] Aucun log disponible"]

        files = ["Connexion.log", "dhcp.log", "tcp.log", "hostapd.log"]
        lines = []

        for f in files:
            path = os.path.join(logs_dir, f)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as fd:
                        lines.extend(fd.readlines())
                except Exception:
                    pass

        cleaned = list(dict.fromkeys(l.strip() for l in lines if l.strip()))
        return cleaned[-20:] if mode == "realtime" else cleaned

    def _get_tag(self, line):
        l = line.upper()
        if "ERROR" in l or "FAILED" in l:
            return "error"
        if "SUCCESS" in l or "STARTED" in l:
            return "success"
        if "WARNING" in l:
            return "warning"
        if "CONNECTION" in l:
            return "connection"
        if "INFO" in l:
            return "info"
        return "normal"

    def _display_logs(self, logs):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")

        if not logs:
            self.text.insert("end", "[INFO] En attente…\n", "info")
        else:
            for line in logs:
                safe = "".join(c if ord(c) >= 32 else "?" for c in line)
                self.text.insert("end", safe + "\n", self._get_tag(safe))

        self.text.config(state="disabled")
        self.text.see("end")

        self.status.config(
            text=f"📊 {len(logs)} log(s) | Mode: {self.current_log_type}"
        )

    # --------------------------------------------------
    # Nettoyage PROPRE
    # --------------------------------------------------
    def on_destroy(self):
        self.auto_refresh_enabled = False
        self._cancel_refresh()
