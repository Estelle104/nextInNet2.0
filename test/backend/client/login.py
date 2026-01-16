import tkinter as tk 
from tkinter import messagebox
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.serveur.main_ui import MainApp
from backend.utils import check_login

def login():
    username = entry_username.get()
    password = entry_password.get()
    if check_login(username, password):
        messagebox.showinfo("Login Successful", "You have been logged in successfully.")
        root.destroy()          # fermer la fenêtre de login
        app = MainApp()         # ouvrir la fenêtre principale
        app.mainloop()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

root = tk.Tk()
root.title("Client Login")
root.geometry("600x300")
root.configure(bg="#f0f0f0")

label_username = tk.Label(root, text="Username:", bg="#f0f0f0")
label_username.pack(pady=(20, 5))
entry_username = tk.Entry(root)
entry_username.pack()

label_password = tk.Label(root, text="Password:", bg="#f0f0f0")
label_password.pack(pady=(10, 5))
entry_password = tk.Entry(root, show="*")
entry_password.pack()

login_button = tk.Button(root, text="Se connecter", command=login,
                         bg="#4CAF50", fg="white", font=("Arial", 12),
                         relief="flat", bd=0, padx=10, pady=5)
login_button.pack(pady=15)

login_button.configure(highlightthickness=0)

root.mainloop()
