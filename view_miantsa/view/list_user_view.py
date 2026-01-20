import tkinter as tk
from data.users_data import users

class ListUserView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Titre
        title = tk.Label(self, text="User List", font=("Arial", 16))
        title.pack(pady=10)

        # Zone d'affichage
        self.list_box = tk.Listbox(self, width=40)
        self.list_box.pack(pady=10)

        # Charger les utilisateurs
        self.load_users()

        # Bouton navigation vers création
        go_create = tk.Button(
            self,
            text="Create New User",
            command=lambda: controller.show_frame("CreateUserView")
        )
        go_create.pack()

    def load_users(self):
        """
        Affiche les utilisateurs existants
        """
        self.list_box.delete(0, tk.END)

        for user in users:
            text = f"Username: {user['username']} | Password: {user['password']}"
            self.list_box.insert(tk.END, text)
