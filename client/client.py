<<<<<<< Updated upstream
import tkinter as tk
from tkinter import messagebox
=======
import socket
import platform  # Nécessaire pour détecter l'OS
>>>>>>> Stashed changes

def valider_login():
    username = entry_username.get()
    password = entry_password.get()
    
    if username == "" or password == "":
        messagebox.showwarning("Champs vides", "Veuillez remplir tous les champs")
    elif username == "admin" and password == "1234":  # Test simple
        messagebox.showinfo("Succès", f"Bienvenue {username}!")
        # Ici vous ajouterez la connexion à votre serveur
        # Par exemple: connect_to_server(username, password)
    else:
        messagebox.showerror("Erreur", "Identifiants incorrects")

def quitter():
    fenetre.destroy()

<<<<<<< Updated upstream
# Création de la fenêtre
fenetre = tk.Tk()
fenetre.title("Login - Connexion Serveur")
fenetre.geometry("500x450")
fenetre.resizable(False, False)  # Fenêtre non redimensionnable
fenetre.configure(bg="#ced4da")

# Frame principal avec un style moderne
main_frame = tk.Frame(fenetre, bg="#adb5bd", bd=2, relief="raised")
main_frame.pack(pady=30, padx=30, fill="both", expand=True)
=======
try:
    client.connect((SERVER_IP, PORT))
    client.send(os_name.encode())
    reponse = client.recv(1024).decode()
    print("Réponse du serveur :", reponse)
>>>>>>> Stashed changes

# Titre
titre = tk.Label(main_frame, text="CONNEXION AU SERVEUR", 
                 font=("Arial", 20, "bold"), 
                 bg="#adb5bd", fg="#1a252f")
titre.pack(pady=(20, 10))

# Frame pour les champs
input_frame = tk.Frame(main_frame, bg="#adb5bd")
input_frame.pack(pady=10, padx=20)

# Username
tk.Label(input_frame, text="Nom d'utilisateur:", 
         font=("Arial", 12), 
         bg="#adb5bd", fg="#1a252f").grid(row=0, column=0, sticky="w", pady=5)
entry_username = tk.Entry(input_frame, font=("Arial", 11), width=23)
entry_username.grid(row=0, column=1, pady=5, padx=10)

# Password
tk.Label(input_frame, text="Mot de passe:", 
         font=("Arial", 12), 
         bg="#adb5bd", fg="#1a252f").grid(row=1, column=0, sticky="w", pady=5)
entry_password = tk.Entry(input_frame, font=("Arial", 11), 
                         show="•", width=23)
entry_password.grid(row=1, column=1, pady=5, padx=10)

# Boutons
button_frame = tk.Frame(main_frame, bg="#adb5bd")
button_frame.pack(pady=20)

btn_login = tk.Button(button_frame, text="Se connecter", 
                     command=valider_login,
                     bg="#3498db", fg="white",
                     font=("Arial", 10, "bold"),
                     width=12, height=1,
                     cursor="hand2")
btn_login.pack(side="left", padx=5)

btn_quit = tk.Button(button_frame, text="Quitter", 
                    command=quitter,
                    bg="#ff6b6b", fg="white",
                    font=("Arial", 10, "bold"),
                    width=12, height=1,
                    cursor="hand2")
btn_quit.pack(side="left", padx=5)

# Focus sur le premier champ
entry_username.focus()

# Lier la touche Entrée à la validation
fenetre.bind('<Return>', lambda event: valider_login())

# Lancer l'application
fenetre.mainloop()