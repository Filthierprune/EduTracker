import tkinter as tk
from tkinter import font
from database import connect_to_db, check_user, register_user
from ui.gui import MainDashboardFrame
from ui.auth_gui import LoginFrame, RegisterFrame

# --- Colores del diseño ---
COLOR_PALETTE = {
    "bg": "#EAEBD0",
    "primary": "#DA6C6C",
    "accent": "#AF3E3E",
    "text": "#333333"
}

class EduTrackerApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db_client = connect_to_db()
        if self.db_client is None:
            print("No se pudo conectar a la base de datos. Saliendo.")
            self.destroy()
            return

        self.title("EduTracker")
        self.geometry("900x650")
        self.configure(bg=COLOR_PALETTE["bg"])

        # Configurar fuentes
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Helvetica", size=10)
        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")

        # Contenedor para las diferentes pantallas (frames)
        container = tk.Frame(self, bg=COLOR_PALETTE["bg"])
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginFrame, RegisterFrame, MainDashboardFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, page_name):
        """Muestra un frame por su nombre."""
        frame = self.frames[page_name]
        frame.tkraise()

    def attempt_login(self, username, password):
        """Intenta iniciar sesión y cambia al dashboard si tiene éxito."""
        from tkinter import messagebox
        user = check_user(username, password)
        if user:
            self.frames["MainDashboardFrame"].set_user(user)
            self.show_frame("MainDashboardFrame")
        else:
            messagebox.showerror("Error de inicio de sesión", "Usuario o contraseña incorrectos.")

    def attempt_register(self, username, password, email):
        """Intenta registrar un nuevo usuario."""
        from tkinter import messagebox
        if not username or not password or not email:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        
        success, message = register_user(username, password, email)
        if success:
            messagebox.showinfo("Éxito", "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
            self.show_frame("LoginFrame")
        else:
            messagebox.showerror("Error de registro", message)


if __name__ == "__main__":
    app = EduTrackerApp()
    app.mainloop()