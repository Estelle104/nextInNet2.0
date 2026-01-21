import tkinter as tk

BG_COLOR = "#eaf2fb"
BTN_COLOR = "#1e88e5"
BTN_HOVER = "#1565c0"
TEXT_COLOR = "#0d47a1"

class CreateUserView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)

        # Titre
        title = tk.Label(
            self,
            text="Create User",
            font=("Arial", 18, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title.pack(pady=20)

        # Username
        tk.Label(
            self,
            text="Username",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 11)
        ).pack()

        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        # Password
        tk.Label(
            self,
            text="Password",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 11)
        ).pack()

        self.password_entry = tk.Entry(self, show="*", width=30)
        self.password_entry.pack(pady=5)

        # Bouton créer
        create_button = tk.Button(
            self,
            text="Create User",
            bg=BTN_COLOR,
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.create_user
        )
        create_button.pack(pady=20)

        # Navigation vers ListUserView
        nav_button = tk.Button(
            self,
            text="Go to List User",
            bg=BTN_COLOR,
            fg="white",
            font=("Arial", 11, "bold"),
            command=lambda: controller.show_frame("ListUserView")
        )
        nav_button.pack(pady=10)

    def create_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        print(f"Creating user: {username} with password: {password}")
