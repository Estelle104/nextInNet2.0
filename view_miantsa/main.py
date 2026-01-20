import tkinter as tk
from tkinter import font

# Import des pages (Views)
from view.create_user_view import CreateUserView
from view.list_user_view import ListUserView


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

        # Boutons de navigation stylisés
        btn_create = tk.Button(
            nav_frame,
            text="➕ Créer Utilisateur",
            command=lambda: self.show_frame("CreateUserView"),
            font=self.button_font,
            bg="#4a90e2",
            fg="white",
            activebackground="#357abd",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            bd=0
        )
        btn_create.pack(side="left", padx=15, pady=10)

        btn_list = tk.Button(
            nav_frame,
            text="📋 Liste Utilisateurs",
            command=lambda: self.show_frame("ListUserView"),
            font=self.button_font,
            bg="#5cb85c",
            fg="white",
            activebackground="#4cae4c",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            bd=0
        )
        btn_list.pack(side="left", padx=5, pady=10)

        # Effet hover sur les boutons
        def on_enter(e, btn, color):
            btn['background'] = color

        def on_leave(e, btn, color):
            btn['background'] = color

        btn_create.bind("<Enter>", lambda e: on_enter(e, btn_create, "#357abd"))
        btn_create.bind("<Leave>", lambda e: on_leave(e, btn_create, "#4a90e2"))
        btn_list.bind("<Enter>", lambda e: on_enter(e, btn_list, "#4cae4c"))
        btn_list.bind("<Leave>", lambda e: on_leave(e, btn_list, "#5cb85c"))

        # ----- Conteneur principal avec bordure -----
        main_container = tk.Frame(self, bg="#f5f7fa")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        container = tk.Frame(main_container, bg="#ffffff", relief="solid", bd=1)
        container.pack(fill="both", expand=True)

        # Configuration de la grille pour le conteneur
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionnaire qui stocke toutes les pages
        self.frames = {}

        # ----- Création des pages -----
        for Page in (CreateUserView, ListUserView):
            page_name = Page.__name__
            frame = Page(container, self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # ----- Pied de page -----
        footer = tk.Frame(self, bg="#e8eef5", height=30)
        footer.pack(fill="x", side="bottom")

        footer_label = tk.Label(
            footer,
            text="© 2026 User Management System",
            font=("Segoe UI", 8),
            bg="#e8eef5",
            fg="#7f8c8d"
        )
        footer_label.pack(pady=8)

        # ----- Page affichée au démarrage -----
        self.show_frame("CreateUserView")

    def show_frame(self, page_name):
        """
        Affiche la page demandée en la mettant au premier plan.
        """
        frame = self.frames[page_name]
        frame.tkraise()


# ----- Point d'entrée du programme -----
if __name__ == "__main__":
    app = App()
    app.mainloop()