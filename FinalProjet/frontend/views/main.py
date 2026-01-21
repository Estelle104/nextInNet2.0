import tkinter as tk
from tkinter import font
import sys

# Ajout du répertoire racine du projet au chemin Python
sys.path.append("/home/andry/Documents/Fianarana/S3/Reseaux/ReseauGit/nextInNet2.0")

# Import des pages (Views)
from FinalProjet.frontend.views.create_user_view import CreateUserView
from FinalProjet.frontend.views.list_user_view import ListUserView
from FinalProjet.frontend.views.logs_view import LogsView


class App(tk.Tk):
    """
    Classe principale de l'application.
    Elle hérite de Tk (fenêtre principale).
    """

    def __init__(self):
        super().__init__()

        # ----- Configuration de la fenêtre -----
        self.title("User Management")
        self.geometry("520x580")
        self.resizable(False, False)

        # Thème moderne avec dégradé subtil
        self.configure(bg="#f5f7fa")

        # ----- Polices personnalisées -----
        self.title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.button_font = font.Font(family="Segoe UI", size=10)
        self.body_font = font.Font(family="Segoe UI", size=9)

        # ----- En-tête de l'application -----
        header = tk.Frame(self, bg="#4a90e2", height=80)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title_label = tk.Label(
            header,
            text="👤 Gestion des Utilisateurs",
            font=self.title_font,
            bg="#4a90e2",
            fg="white",
            pady=20
        )
        title_label.pack()

        # ----- Barre de navigation -----
        nav_frame = tk.Frame(self, bg="#ffffff", height=50)
        nav_frame.pack(fill="x", side="top")
        nav_frame.pack_propagate(False)

        # ----- Conteneur principal pour les vues -----
        self.container = tk.Frame(self, bg="#f5f7fa")
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (CreateUserView, ListUserView, LogsView):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("CreateUserView")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

