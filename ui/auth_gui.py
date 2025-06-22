import tkinter as tk
from tkinter import font

# --- Colores del diseño ---
COLOR_PALETTE = {
    "bg": "#EAEBD0",
    "primary": "#DA6C6C",
    "accent": "#AF3E3E",
    "entry_bg": "#F5E6E6",
    "text": "#333333",
    "light_text": "#555555"
}

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_PALETTE["bg"])
        self.controller = controller

        main_frame = tk.Frame(self, bg=COLOR_PALETTE["primary"], bd=5, relief="flat", width=400, height=450)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        main_frame.pack_propagate(False)

        title = tk.Label(main_frame, text="Login", bg=COLOR_PALETTE["primary"], fg=COLOR_PALETTE["text"], font=controller.title_font)
        title.pack(pady=(40, 20))

        # Usuario
        tk.Label(main_frame, text="Usuario", bg=COLOR_PALETTE["primary"], fg=COLOR_PALETTE["text"]).pack(padx=50, anchor="w")
        self.username_entry = tk.Entry(main_frame, bg=COLOR_PALETTE["entry_bg"], fg=COLOR_PALETTE["text"], relief="flat", font=("Helvetica", 12))
        self.username_entry.pack(pady=5, padx=50, fill="x")

        # Contraseña
        tk.Label(main_frame, text="Contraseña", bg=COLOR_PALETTE["primary"], fg=COLOR_PALETTE["text"]).pack(padx=50, anchor="w")
        self.password_entry = tk.Entry(main_frame, show="*", bg=COLOR_PALETTE["entry_bg"], fg=COLOR_PALETTE["text"], relief="flat", font=("Helvetica", 12))
        self.password_entry.pack(pady=5, padx=50, fill="x")

        # Botón Iniciar Sesión
        login_btn = tk.Button(main_frame, text="Iniciar Sesión", bg=COLOR_PALETTE["accent"], fg="white", relief="flat", font=("Helvetica", 11, "bold"),
                              command=lambda: controller.attempt_login(self.username_entry.get(), self.password_entry.get()))
        login_btn.pack(pady=20, ipadx=10)

        # Botón Crear Cuenta
        register_btn = tk.Button(main_frame, text="Crear nueva cuenta", bg=COLOR_PALETTE["primary"], fg=COLOR_PALETTE["light_text"], relief="flat", font=("Helvetica", 9, "underline"),
                                 command=lambda: controller.show_frame("RegisterFrame"))
        register_btn.pack(pady=10)

class RegisterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_PALETTE["bg"])
        self.controller = controller

        main_frame = tk.Frame(self, bg=COLOR_PALETTE["primary"], bd=5, relief="flat", width=400, height=500)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        main_frame.pack_propagate(False)

        title = tk.Label(main_frame, text="Crea una cuenta", bg=COLOR_PALETTE["primary"], fg=COLOR_PALETTE["text"], font=controller.title_font)
        title.pack(pady=(40, 20))

        # Usuario
        tk.Label(main_frame, text="Usuario", bg=COLOR_PALETTE["primary"], fg=COLOR_PALETTE["text"]).pack(padx=50, anchor="w")
        self.username_entry = tk.Entry(main_frame, bg=COLOR_PALETTE["entry_bg"], fg=COLOR_PALETTE["text"], relief="flat", font=("Helvetica", 12))
        self.username_entry.pack(pady=5, padx=50, fill="x")

        # Email
        tk.Label(main_frame, text="Email", bg=COLOR_PALETTE["primary"], fg=COLOR_PALETTE["text"]).pack(padx=50, anchor="w")
        self.email_entry = tk.Entry(main_frame, bg=COLOR_PALETTE["entry_bg"], fg=COLOR_PALETTE["text"], relief="flat", font=("Helvetica", 12))
        self.email_entry.pack(pady=5, padx=50, fill="x")

        # Contraseña
        tk.Label(main_frame, text="Contraseña", bg=COLOR_PALETTE["primary"], fg=COLOR_PALETTE["text"]).pack(padx=50, anchor="w")
        self.password_entry = tk.Entry(main_frame, show="*", bg=COLOR_PALETTE["entry_bg"], fg=COLOR_PALETTE["text"], relief="flat", font=("Helvetica", 12))
        self.password_entry.pack(pady=5, padx=50, fill="x")

        # Botón Registrarse
        register_btn = tk.Button(main_frame, text="Registrarte", bg=COLOR_PALETTE["accent"], fg="white", relief="flat", font=("Helvetica", 11, "bold"),
                                 command=lambda: controller.attempt_register(self.username_entry.get(), self.password_entry.get(), self.email_entry.get()))
        register_btn.pack(pady=20, ipadx=10)

        # Botón ¿Ya tienes cuenta?
        login_btn = tk.Button(main_frame, text="¿Ya tienes cuenta? Inicia sesión", bg=COLOR_PALETTE["primary"], fg=COLOR_PALETTE["light_text"], relief="flat", font=("Helvetica", 9, "underline"),
                              command=lambda: controller.show_frame("LoginFrame"))
        login_btn.pack(pady=10)