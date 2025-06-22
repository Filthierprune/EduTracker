import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from PIL import Image, ImageTk
import requests
from io import BytesIO
from datetime import datetime

# Importar clases del proyecto
from api.books_api import BooksAPI
from api.quotes_api import QuotesAPI
from database.mongo_client import MongoRepository
from models.estudio import Estudio
from models.meta import Meta, PeriodoMeta

# --- Colores del diseño ---
COLOR_PALETTE = {
    "bg": "#EAEBD0",
    "primary": "#DA6C6C",
    "accent": "#AF3E3E",
    "text": "#333333"
}

class MainDashboardFrame(tk.Frame):
    """Frame principal que contiene el dashboard de la aplicación."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_PALETTE["bg"])
        self.controller = controller
        self.db_client = controller.db_client
        self.current_user_id = None # Se establecerá después del login

    def set_user(self, user_data):
        """Configura el usuario actual y carga la interfaz del dashboard."""
        self.current_user_id = user_data["username"]
        self.controller.title(f"EduTracker - Usuario: {self.current_user_id}")
        
        # Limpiar widgets anteriores si se vuelve a llamar
        for widget in self.winfo_children():
            widget.destroy()

        # Inicializar APIs y Repositorios
        self.books_api = BooksAPI()
        self.quotes_api = QuotesAPI()
        self.estudio_repo = MongoRepository(self.db_client, 'sesiones_estudio', Estudio)
        self.meta_repo = MongoRepository(self.db_client, 'metas', Meta)

        # Crear la interfaz del dashboard
        self.crear_header()
        self.crear_pestañas_dashboard()

    def crear_header(self):
        header_frame = tk.Frame(self, bg=COLOR_PALETTE["bg"])
        header_frame.pack(fill="x", pady=10, padx=20)
        
        # Placeholder para imagen de perfil
        # profile_img = ... (código para cargar imagen)
        # tk.Label(header_frame, image=profile_img).pack(side="left")

        tk.Label(header_frame, text=f"Bienvenido, {self.current_user_id}", font=("Helvetica", 16, "bold"), bg=COLOR_PALETTE["bg"]).pack(side="left", padx=10)
        
        logout_btn = tk.Button(header_frame, text="Cerrar Sesión", bg=COLOR_PALETTE["accent"], fg="white", relief="flat",
                               command=lambda: self.controller.show_frame("LoginFrame"))
        logout_btn.pack(side="right")

    def crear_pestañas_dashboard(self):
        # Usamos un Notebook (pestañas) para organizar el contenido del dashboard
        self.notebook = ttk.Notebook(self)
        
        # Estilo para las pestañas
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Helvetica", 11), padding=[10, 5])
        style.configure("TNotebook", background=COLOR_PALETTE["bg"], borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", COLOR_PALETTE["primary"])], foreground=[("selected", "white")])

        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        self.crear_pestaña_estudio()
        self.crear_pestaña_metas()
        self.crear_pestaña_libros()
        self.crear_pestaña_citas()

    # --- Pestaña de Sesiones de Estudio (Tareas Diarias) ---
    def crear_pestaña_estudio(self):
        tab_estudio = ttk.Frame(self.notebook)
        self.notebook.add(tab_estudio, text="Seguimiento de Estudio")

        # Formulario para nueva sesión
        form_frame = ttk.LabelFrame(tab_estudio, text="Registrar Nueva Sesión de Estudio")
        form_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(form_frame, text="Materia:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.materia_estudio_entry = ttk.Entry(form_frame, width=30)
        self.materia_estudio_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Duración (minutos):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.duracion_entry = ttk.Entry(form_frame, width=10)
        self.duracion_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Notas:").grid(row=2, column=0, padx=5, pady=5, sticky="nw")
        self.notas_text = scrolledtext.ScrolledText(form_frame, width=40, height=5)
        self.notas_text.grid(row=2, column=1, padx=5, pady=5)

        registrar_btn = ttk.Button(form_frame, text="Guardar Sesión", command=self.registrar_sesion_estudio)
        registrar_btn.grid(row=3, column=1, padx=5, pady=10, sticky="e")

        # Lista de sesiones
        list_frame = ttk.LabelFrame(tab_estudio, text="Historial de Sesiones")
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.estudio_tree = ttk.Treeview(list_frame, columns=("materia", "duracion", "fecha", "notas"), show="headings")
        self.estudio_tree.heading("materia", text="Materia")
        self.estudio_tree.heading("duracion", text="Duración (min)")
        self.estudio_tree.heading("fecha", text="Fecha y Hora")
        self.estudio_tree.heading("notas", text="Notas")
        self.estudio_tree.pack(fill="both", expand=True)
        
        self.cargar_sesiones_estudio()

    # --- Pestaña de Metas (Hábitos / Tareas Pendientes) ---
    def crear_pestaña_metas(self):
        tab_metas = ttk.Frame(self.notebook)
        self.notebook.add(tab_metas, text="Metas de Estudio")

        # Formulario para nueva meta
        form_frame = ttk.LabelFrame(tab_metas, text="Crear Nueva Meta")
        form_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(form_frame, text="Materia:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.materia_meta_entry = ttk.Entry(form_frame, width=30)
        self.materia_meta_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Minutos Objetivo:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.objetivo_entry = ttk.Entry(form_frame, width=10)
        self.objetivo_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Periodo:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.periodo_combobox = ttk.Combobox(form_frame, values=[p.value for p in PeriodoMeta])
        self.periodo_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.periodo_combobox.set(PeriodoMeta.SEMANAL.value)

        registrar_btn = ttk.Button(form_frame, text="Guardar Meta", command=self.registrar_meta)
        registrar_btn.grid(row=3, column=1, padx=5, pady=10, sticky="e")

        # Lista de metas
        list_frame = ttk.LabelFrame(tab_metas, text="Mis Metas")
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.metas_tree = ttk.Treeview(list_frame, columns=("materia", "objetivo", "periodo", "progreso", "estado"), show="headings")
        self.metas_tree.heading("materia", text="Materia")
        self.metas_tree.heading("objetivo", text="Objetivo (min)")
        self.metas_tree.heading("periodo", text="Periodo")
        self.metas_tree.heading("progreso", text="Progreso")
        self.metas_tree.heading("estado", text="Estado")
        self.metas_tree.pack(fill="both", expand=True)

        self.cargar_metas()

    # --- Pestaña de Búsqueda de Libros ---
    def crear_pestaña_libros(self):
        tab_libros = ttk.Frame(self.notebook)
        self.notebook.add(tab_libros, text="Búsqueda de Libros")

        # Barra de búsqueda
        search_frame = ttk.Frame(tab_libros)
        search_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(search_frame, text="Buscar:").pack(side="left", padx=5)
        self.book_query_entry = ttk.Entry(search_frame, width=50)
        self.book_query_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_btn = ttk.Button(search_frame, text="Buscar", command=self.buscar_libros)
        search_btn.pack(side="left", padx=5)

        # Frame para resultados con scroll
        canvas = tk.Canvas(tab_libros)
        scrollbar = ttk.Scrollbar(tab_libros, orient="vertical", command=canvas.yview)
        self.book_results_frame = ttk.Frame(canvas)

        self.book_results_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.book_results_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

    # --- Pestaña de Citas Motivacionales ---
    def crear_pestaña_citas(self):
        tab_citas = ttk.Frame(self.notebook)
        self.notebook.add(tab_citas, text="Citas Motivacionales")

        # Frame de control
        control_frame = ttk.Frame(tab_citas)
        control_frame.pack(pady=20)

        ttk.Button(control_frame, text="Cita Aleatoria", command=self.obtener_cita_aleatoria).pack(side="left", padx=10)
        ttk.Button(control_frame, text="Cita del Día", command=self.obtener_cita_del_dia).pack(side="left", padx=10)

        # Frame para mostrar la cita
        quote_frame = ttk.LabelFrame(tab_citas, text="Cita")
        quote_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.quote_text = tk.Label(quote_frame, text="", font=("Helvetica", 14, "italic"), wraplength=700, justify="center")
        self.quote_text.pack(pady=20, padx=10)
        
        self.author_text = tk.Label(quote_frame, text="", font=("Helvetica", 12, "bold"))
        self.author_text.pack(pady=10)

        self.obtener_cita_aleatoria() # Cargar una al inicio

    def cargar_sesiones_estudio(self):
        for i in self.estudio_tree.get_children():
            self.estudio_tree.delete(i)
        
        sesiones = self.estudio_repo.find({"usuario_id": self.current_user_id})
        for sesion in sorted(sesiones, key=lambda s: s.fecha_hora, reverse=True):
            self.estudio_tree.insert("", "end", values=(
                sesion.materia,
                sesion.duracion_minutos,
                sesion.fecha_hora.strftime("%Y-%m-%d %H:%M"),
                sesion.notas or ""
            ))
            
    def registrar_sesion_estudio(self):
        materia = self.materia_estudio_entry.get()
        duracion_str = self.duracion_entry.get()
        notas = self.notas_text.get("1.0", tk.END).strip()

        if not materia or not duracion_str:
            messagebox.showerror("Error", "La materia y la duración son obligatorias.")
            return
        
        try:
            duracion = int(duracion_str)
            nueva_sesion = Estudio(self.current_user_id, materia, duracion, notas)
            self.estudio_repo.save(nueva_sesion)
            messagebox.showinfo("Éxito", "Sesión de estudio registrada correctamente.")
            self.cargar_sesiones_estudio()
            self.materia_estudio_entry.delete(0, tk.END)
            self.duracion_entry.delete(0, tk.END)
            self.notas_text.delete("1.0", tk.END)
        except ValueError:
            messagebox.showerror("Error", "La duración debe ser un número entero.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la sesión: {e}")

    def cargar_metas(self):
        for i in self.metas_tree.get_children():
            self.metas_tree.delete(i)
        
        metas = self.meta_repo.find({"usuario_id": self.current_user_id})
        for meta in sorted(metas, key=lambda m: m.fecha_inicio, reverse=True):
            try:
                ahora = datetime.now()
                if ahora > meta.fecha_fin and not meta.completada:
                    estado = "Vencida"
                    progreso_str = "N/A"
                elif meta.completada:
                    estado = "Completada"
                    progreso_str = "100%"
                else:
                    estado = "Activa"
                    sesiones = self.estudio_repo.find({
                        "usuario_id": self.current_user_id,
                        "materia": meta.materia,
                        "fecha_hora": {"$gte": meta.fecha_inicio, "$lt": meta.fecha_fin}
                    })
                    minutos_logrados = sum(s.duracion_minutos for s in sesiones)
                    progreso = (minutos_logrados / meta.minutos_objetivo) * 100 if meta.minutos_objetivo > 0 else 100
                    progreso_str = f"{minutos_logrados} / {meta.minutos_objetivo} min ({progreso:.1f}%)"

                self.metas_tree.insert("", "end", values=(
                    meta.materia,
                    meta.minutos_objetivo,
                    meta.periodo.value,
                    progreso_str,
                    estado
                ))
            except Exception as e:
                print(f"Error al procesar una meta. Datos: {getattr(meta, '__dict__', 'N/A')}. Error: {e}")
                self.metas_tree.insert("", "end", values=("Error", "Dato inválido", "", "", ""))

    def registrar_meta(self):
        materia = self.materia_meta_entry.get()
        objetivo_str = self.objetivo_entry.get()
        periodo_str = self.periodo_combobox.get()

        if not materia or not objetivo_str or not periodo_str:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            objetivo = int(objetivo_str)
            periodo = PeriodoMeta(periodo_str)
            nueva_meta = Meta(self.current_user_id, materia, objetivo, periodo)
            self.meta_repo.save(nueva_meta)
            messagebox.showinfo("Éxito", "Meta registrada correctamente.")
            self.cargar_metas()
            self.materia_meta_entry.delete(0, tk.END)
            self.objetivo_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Los minutos objetivo deben ser un número entero.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la meta: {e}")

    def buscar_libros(self):
        query = self.book_query_entry.get()
        if not query:
            return

        for widget in self.book_results_frame.winfo_children():
            widget.destroy()
            
        try:
            libros = self.books_api.search_books(query, limit=10)
            if not libros:
                ttk.Label(self.book_results_frame, text="No se encontraron libros.").pack(pady=20)
                return

            for libro in libros:
                self.mostrar_resultado_libro(libro)
        except Exception as e:
            messagebox.showerror("Error de API", f"No se pudo contactar con la API de OpenLibrary: {e}")

    def mostrar_resultado_libro(self, libro):
        item_frame = ttk.Frame(self.book_results_frame, borderwidth=2, relief="groove")
        item_frame.pack(padx=10, pady=5, fill="x")

        cover_label = ttk.Label(item_frame)
        cover_label.grid(row=0, column=0, rowspan=3, padx=10, pady=5)

        # Cargar imagen de portada
        if "cover_url" in libro:
            try:
                response = requests.get(libro["cover_url"], stream=True)
                response.raise_for_status()
                img_data = response.content
                img = Image.open(BytesIO(img_data))
                img.thumbnail((100, 150))
                photo = ImageTk.PhotoImage(img)
                cover_label.config(image=photo)
                cover_label.image = photo
            except Exception:
                cover_label.config(text="[Sin Portada]")

        ttk.Label(item_frame, text=libro.get('title', 'N/A'), font=("Helvetica", 12, "bold")).grid(row=0, column=1, sticky="w")
        ttk.Label(item_frame, text=f"Autor(es): {', '.join(libro.get('authors', ['N/A']))}").grid(row=1, column=1, sticky="w")
        ttk.Label(item_frame, text=f"Año de publicación: {libro.get('year', 'N/A')}").grid(row=2, column=1, sticky="w")

    def mostrar_cita(self, cita_info):
        if cita_info:
            self.quote_text.config(text=f'"{cita_info["quote"]}"')
            self.author_text.config(text=f"— {cita_info['author']}")
        else:
            self.quote_text.config(text="No se pudo obtener la cita.")
            self.author_text.config(text="")

    def obtener_cita_aleatoria(self):
        cita = self.quotes_api.get_random_quote()
        self.mostrar_cita(cita)

    def obtener_cita_del_dia(self):
        cita = self.quotes_api.get_daily_quote()
        self.mostrar_cita(cita)