import tkinter as tk
from users_view import UsersView
from logs_view import LogsView
from notif_view import NotifView
from assets.theme import *

class Dashboard(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self.pack(fill="both", expand=True)

        nav = tk.Frame(self, bg=SECONDARY)
        nav.pack(fill="x")

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)

        tk.Button(nav, text="Gestion User", command=self.show_users).pack(side="left", padx=10)
        tk.Button(nav, text="Gestion Log", command=self.show_logs).pack(side="left", padx=10)
        tk.Button(nav, text="Notifications", command=self.show_notifs).pack(side="left", padx=10)

        self.show_users()

    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_users(self):
        self.clear()
        UsersView(self.container)

    def show_logs(self):
        self.clear()
        LogsView(self.container)

    def show_notifs(self):
        self.clear()
        NotifView(self.container)
