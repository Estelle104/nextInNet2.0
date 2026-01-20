import tkinter as tk
from assets.theme import *
import socket  # Import socket for TCP communication

class LogsView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self.pack(fill="both", expand=True)

        # Title
        tk.Label(self, text="Logs en temps réel", font=("Arial", 16), bg=BG).pack(pady=10)

        # Tabs for real-time and history logs
        self.tab_frame = tk.Frame(self, bg=BG)
        self.tab_frame.pack(fill="x", pady=5)

        self.realtime_button = tk.Button(self.tab_frame, text="Temps réel", bg=PRIMARY, fg=TEXT, command=self.show_realtime_logs)
        self.realtime_button.pack(side="left", padx=5)

        self.history_button = tk.Button(self.tab_frame, text="Historique", bg=SECONDARY, fg=TEXT, command=self.show_history_logs)
        self.history_button.pack(side="left", padx=5)

        # Log display area
        self.log_display = tk.Text(self, height=20, state="disabled", bg=BG, fg=TEXT, wrap="word")
        self.log_display.pack(fill="both", expand=True, padx=10, pady=10)

        # Show real-time logs by default
        self.show_realtime_logs()

    def show_realtime_logs(self):
        self.update_tab_colors(self.realtime_button, self.history_button)
        logs = self.fetch_logs("realtime")  # Fetch real-time logs via TCP
        self.display_logs(logs)

    def show_history_logs(self):
        self.update_tab_colors(self.history_button, self.realtime_button)
        logs = self.fetch_logs("history")  # Fetch historical logs via TCP
        self.display_logs(logs)

    def update_tab_colors(self, active_button, inactive_button):
        active_button.config(bg=PRIMARY, fg=TEXT)
        inactive_button.config(bg=SECONDARY, fg=TEXT)

    def fetch_logs(self, log_type):
        try:
            # Connect to the TCP server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", 5050))  # Connect to the TCP server on port 5050
                s.sendall(log_type.encode())  # Send the log type (e.g., "realtime" or "history")
                data = s.recv(4096).decode()  # Receive the logs from the server
            return data.splitlines()  # Split the logs into a list of lines
        except Exception as e:
            return [f"[ERROR] Impossible de récupérer les logs : {e}"]

    def display_logs(self, logs):
        self.log_display.config(state="normal")
        self.log_display.delete("1.0", "end")
        for log in logs:
            if "[SUCCESS]" in log:
                self.log_display.insert("end", log + "\n", "success")
            elif "[ERROR]" in log:
                self.log_display.insert("end", log + "\n", "error")
            else:
                self.log_display.insert("end", log + "\n")

        self.log_display.tag_config("success", foreground="green")
        self.log_display.tag_config("error", foreground="red")
        self.log_display.config(state="disabled")
