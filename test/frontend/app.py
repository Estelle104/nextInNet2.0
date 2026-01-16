import tkinter as tk
from login_view import LoginView
from dashboard_view import Dashboard

root = tk.Tk()
root.title("Application de Surveillance Réseau")
root.geometry("900x600")

def open_dashboard():
    for w in root.winfo_children():
        w.destroy()
    Dashboard(root)

LoginView(root, open_dashboard)
root.mainloop()
