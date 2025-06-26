import tkinter as tk
import platform
import os
from tkinter import messagebox
from tkinter import ttk, simpledialog, colorchooser
from datetime import datetime, timedelta
import time
from database.mongo_client import MongoRepository
from models.estudio import Estudio
from models.meta import Meta, PeriodoMeta
from database import get_subjects, add_subject, delete_subject
from bson.objectid import ObjectId
from utils.chart import ProgressChart
from api.quotes_api import QuotesAPI  # Import movido al inicio

# Solo importar winsound en Windows
if os.name == 'nt':
    import winsound

# --- Colores del diseño ---
COLOR_PALETTE = {
    "bg": "#8F8DFF",
    "primary": "#10004F",
    "accent": "#03373A",
    "text": "#000000",
    "widget_bg": "#A06DF9",
    "work": "#042809",    # Verde para trabajo
    "break": "#780022"    # Azul para descanso
}

class MainDashboardFrame(tk.Frame):
    """Frame principal rediseñado que contiene el dashboard de la aplicación."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_PALETTE["bg"])
        self.controller = controller
        self.db_client = controller.db_client
        self.current_user_id = None
        self.pomodoro_running = False
        self.pomodoro_phase = "work"  # 'work' o 'break'
        self.pomodoro_time_left = 25 * 60  # 25 minutos en segundos
        self.break_time = 5 * 60  # Valor por defecto

    def show_alert(self, title, message):
        """Muestra una alerta emergente con sonido."""
        try:
            if os.name == 'nt':  # Windows
                winsound.MessageBeep()
            else:  # macOS/Linux
                os.system('afplay /System/Library/Sounds/Ping.aiff')
        except Exception:
            pass
        
        alert = tk.Toplevel(self)
        alert.title(title)
        alert.geometry("300x150")
        alert.transient(self)
        alert.grab_set()
        
        tk.Label(alert, text=message, font=("Helvetica", 14)).pack(pady=20)
        tk.Button(alert, text="OK", command=alert.destroy, width=10).pack(pady=10)
    
    def set_user(self, user_data):
        """Configura el usuario actual y carga la interfaz del dashboard."""
        self.current_user_id = user_data["username"]
        self.controller.title(f"EduTracker - Usuario: {self.current_user_id}")
        
        for widget in self.winfo_children():
            widget.destroy()

        self.estudio_repo = MongoRepository(self.db_client, 'sesiones_estudio', Estudio)
        self.meta_repo = MongoRepository(self.db_client, 'metas', Meta)
        self.subject_map = {}  # Inicializar mapa de materias

        self.create_dashboard_layout()
        self.refresh_data()

    def refresh_data(self):
        """Recarga todos los datos del dashboard."""
        self.load_recent_sessions()
        self.load_goals_summary()
        self.progress_chart.create_chart(self.estudio_repo)  # Actualizar gráfica

    def create_dashboard_layout(self):
        # --- Header ---
        header_frame = tk.Frame(self, bg=COLOR_PALETTE["bg"])
        header_frame.pack(fill="x", pady=10, padx=20)
        
        tk.Label(header_frame, text=f"Bienvenido, {self.current_user_id}", font=("Helvetica", 16, "bold"), 
                bg=COLOR_PALETTE["bg"], fg="black").pack(side="left", padx=10)
        
        logout_btn = tk.Button(header_frame, text="Cerrar Sesión", bg=COLOR_PALETTE["accent"], 
                              fg="black", relief="flat", command=lambda: self.controller.show_frame("LoginFrame"))
        logout_btn.pack(side="right", padx=5)
        
        goals_btn = tk.Button(header_frame, text="Gestionar Metas", bg=COLOR_PALETTE["primary"], 
                             fg="black", relief="flat", command=self.open_goal_manager)
        goals_btn.pack(side="right", padx=5)
        
        subjects_btn = tk.Button(header_frame, text="Gestionar Materias", bg=COLOR_PALETTE["primary"], 
                                fg="black", relief="flat", command=self.open_subject_manager)
        subjects_btn.pack(side="right", padx=5)

        # --- Contenedor Principal ---
        main_container = tk.Frame(self, bg=COLOR_PALETTE["bg"])
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # --- Panel Izquierdo (Acciones rápidas) ---
        left_panel = tk.Frame(main_container, bg=COLOR_PALETTE["bg"])
        left_panel.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        
        # Widget de Iniciar Sesión de Estudio
        self.create_study_session_widget(left_panel)
        
        # Widget de Temporizador Pomodoro
        self.create_pomodoro_widget(left_panel)

        # --- Panel Derecho (Información) ---
        right_panel = tk.Frame(main_container, bg=COLOR_PALETTE["bg"])
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Resumen de Metas
        self.goals_frame = tk.LabelFrame(right_panel, text="Resumen de Metas", 
                                        padx=10, pady=10, bg=COLOR_PALETTE["widget_bg"])
        self.goals_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Historial de Sesiones
        sessions_frame = tk.LabelFrame(right_panel, text="Historial de Sesiones Recientes", 
                                     padx=10, pady=10, bg=COLOR_PALETTE["widget_bg"])
        sessions_frame.grid(row=1, column=0, sticky="nsew")
        
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=("materia", "duracion", "fecha"), show="headings")
        self.sessions_tree.heading("materia", text="Materia")
        self.sessions_tree.heading("duracion", text="Duración (min)")
        self.sessions_tree.heading("fecha", text="Fecha")
        self.sessions_tree.column("materia", width=150)
        self.sessions_tree.column("duracion", width=100)
        self.sessions_tree.column("fecha", width=150)
        self.sessions_tree.pack(fill="both", expand=True)

        # --- Panel Inferior (Gráfica) ---
        bottom_panel = tk.Frame(self, bg=COLOR_PALETTE["bg"])
        bottom_panel.pack(fill="x", padx=20, pady=10)
    
        # Gráfica de progreso
        self.chart_frame = tk.Frame(bottom_panel, bg=COLOR_PALETTE["widget_bg"], height=300)
        self.chart_frame.pack(fill="both", expand=True, pady=(0, 10))
        self.progress_chart = ProgressChart(self.chart_frame, self.current_user_id)
        
        # Cargar datos iniciales
        self.refresh_data()

    def create_study_session_widget(self, parent):
        """Crea el widget para registrar una nueva sesión de estudio."""
        widget_frame = tk.LabelFrame(parent, text="Nueva Sesión de Estudio", 
                                   padx=10, pady=10, bg=COLOR_PALETTE["widget_bg"])
        widget_frame.pack(fill="x")

        ttk.Label(widget_frame, text="Materia:", background=COLOR_PALETTE["widget_bg"]).grid(row=0, column=0, sticky="w", pady=2)
        self.materia_combobox = ttk.Combobox(widget_frame, state="readonly")
        self.materia_combobox.grid(row=0, column=1, sticky="ew", pady=2, padx=5)

        ttk.Label(widget_frame, text="Duración (min):", background=COLOR_PALETTE["widget_bg"]).grid(row=1, column=0, sticky="w", pady=2)
        self.duracion_entry = ttk.Entry(widget_frame)
        self.duracion_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=5)

        ttk.Label(widget_frame, text="Notas:", background=COLOR_PALETTE["widget_bg"]).grid(row=2, column=0, sticky="nw", pady=2)
        self.notas_entry = tk.Text(widget_frame, height=4, width=30)
        self.notas_entry.grid(row=2, column=1, sticky="ew", pady=2, padx=5)

        save_btn = ttk.Button(widget_frame, text="Guardar Sesión", command=self.registrar_sesion_estudio)
        save_btn.grid(row=3, column=1, sticky="e", pady=10)
        
        self.load_subjects_into_combobox()

    def create_pomodoro_widget(self, parent):
        """Crea un temporizador Pomodoro funcional."""
        pomodoro_frame = tk.LabelFrame(parent, text="Temporizador Pomodoro", 
                                     padx=10, pady=10, bg=COLOR_PALETTE["widget_bg"])
        pomodoro_frame.pack(fill="x", pady=10)
        
        self.pomodoro_label = tk.Label(
            pomodoro_frame, 
            text=self.format_time(self.pomodoro_time_left), 
            font=("Helvetica", 24, "bold"),
            bg=COLOR_PALETTE["widget_bg"],
            fg=COLOR_PALETTE["work"]
        )
        self.pomodoro_label.pack(pady=5)
        
        self.phase_label = tk.Label(
            pomodoro_frame, 
            text="Trabajo", 
            font=("Helvetica", 12),
            bg=COLOR_PALETTE["widget_bg"],
            fg=COLOR_PALETTE["work"]
        )
        self.phase_label.pack()
        
        # Frase motivadora
        self.quote_frame = tk.Frame(pomodoro_frame, bg=COLOR_PALETTE["widget_bg"])
        self.quote_frame.pack(fill="x", pady=10)
    
        self.quote_label = tk.Label(
            self.quote_frame, 
            text="",
            wraplength=250,
            justify="center",
            font=("Helvetica", 10, "italic"),
            bg=COLOR_PALETTE["widget_bg"],
            fg=COLOR_PALETTE["text"]
        )
        self.quote_label.pack()
    
        # Iniciar actualización de frases motivadoras
        self.update_quote()
        
        buttons_frame = tk.Frame(pomodoro_frame, bg=COLOR_PALETTE["widget_bg"])
        buttons_frame.pack(pady=10)
        
        self.start_button = tk.Button(
            buttons_frame, 
            text="Iniciar", 
            command=self.start_pomodoro,
            bg=COLOR_PALETTE["primary"], 
            fg="black",
            width=8
        )
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = tk.Button(
            buttons_frame, 
            text="Pausar", 
            command=self.pause_pomodoro,
            bg=COLOR_PALETTE["accent"], 
            fg="black",
            width=8,
            state=tk.DISABLED
        )
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.reset_button = tk.Button(
            buttons_frame, 
            text="Reiniciar", 
            command=self.reset_pomodoro,
            bg=COLOR_PALETTE["accent"], 
            fg="black",
            width=8
        )
        self.reset_button.grid(row=0, column=2, padx=5)
        
        phase_frame = tk.Frame(pomodoro_frame, bg=COLOR_PALETTE["widget_bg"])
        phase_frame.pack(pady=5)
        
        tk.Label(phase_frame, text="Tiempo:", bg=COLOR_PALETTE["widget_bg"]).grid(row=0, column=0, padx=5)
        
        # Botones para seleccionar duración de trabajo
        tk.Button(
            phase_frame, 
            text="1 min", 
            command=lambda: self.set_pomodoro_time(1),
            bg=COLOR_PALETTE["work"], 
            fg="white",
            width=6
        ).grid(row=0, column=1, padx=2)
        
        tk.Button(
            phase_frame, 
            text="5 min", 
            command=lambda: self.set_pomodoro_time(5),
            bg=COLOR_PALETTE["work"], 
            fg="white",
            width=6
        ).grid(row=0, column=2, padx=2)
        
        tk.Button(
            phase_frame,
            text="25 min",
            command=lambda: self.set_pomodoro_time(25),
            bg=COLOR_PALETTE["work"],
            fg="white",
            width=6
        ).grid(row=0, column=3, padx=2)
        
        # Botón para descanso (ejemplo: 10 min)
        tk.Button(
            phase_frame, 
            text="10 min (descanso)", 
            command=lambda: self.set_pomodoro_time(10),
            bg=COLOR_PALETTE["break"], 
            fg="white",
            width=14
        ).grid(row=0, column=4, padx=2)

    def update_quote(self):
        """Actualiza la frase motivadora periódicamente."""
        try:
            quotes_api = QuotesAPI()
            quote = quotes_api.get_random_quote()
            if quote:
                self.quote_label.config(text=f'"{quote["quote"]}"\n- {quote["author"]}')
        except Exception as e:
            print(f"Error obteniendo frase: {e}")
            self.quote_label.config(text="La disciplina es el puente entre metas y logros.\n- Jim Rohn")
        
        # Actualizar cada 2 minutos
        self.after(120000, self.update_quote)

    def format_time(self, seconds):
        """Formatea segundos a MM:SS."""
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def set_pomodoro_time(self, minutes):
        """Establece el tiempo de trabajo."""
        if not self.pomodoro_running:
            self.pomodoro_time_left = minutes * 60
            self.pomodoro_label.config(text=self.format_time(self.pomodoro_time_left))

    def start_pomodoro(self):
        """Inicia el temporizador Pomodoro."""
        if not self.pomodoro_running:
            self.pomodoro_running = True
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.update_pomodoro()

    def pause_pomodoro(self):
        """Pausa el temporizador Pomodoro."""
        if self.pomodoro_running:
            self.pomodoro_running = False
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)

    def reset_pomodoro(self):
        """Reinicia el temporizador Pomodoro."""
        self.pomodoro_running = False
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        
        if self.pomodoro_phase == "work":
            self.pomodoro_time_left = 25 * 60
            self.phase_label.config(text="Trabajo", fg=COLOR_PALETTE["work"])
            self.pomodoro_label.config(fg=COLOR_PALETTE["work"])
        else:
            self.pomodoro_phase = "work"
            self.pomodoro_time_left = 25 * 60
            self.phase_label.config(text="Trabajo", fg=COLOR_PALETTE["work"])
            self.pomodoro_label.config(fg=COLOR_PALETTE["work"])
        
        self.pomodoro_label.config(text=self.format_time(self.pomodoro_time_left))

    def update_pomodoro(self):
        """Actualiza el temporizador Pomodoro."""
        if self.pomodoro_running:
            if self.pomodoro_time_left > 0:
                self.pomodoro_time_left -= 1
                self.pomodoro_label.config(text=self.format_time(self.pomodoro_time_left))
                self.after(1000, self.update_pomodoro)
            else:
                # Cambiar de fase
                if self.pomodoro_phase == "work":
                    # Mostrar alerta de fin de trabajo
                    self.show_alert("¡Tiempo de trabajo completado!", "Es hora de un descanso")
                    self.pomodoro_phase = "break"
                    self.pomodoro_time_left = self.break_time  # Usar break_time
                    self.phase_label.config(text="Descanso", fg=COLOR_PALETTE["break"])
                    self.pomodoro_label.config(fg=COLOR_PALETTE["break"])
                else:
                    # Mostrar alerta de fin de descanso
                    self.show_alert("¡Descanso terminado!", "Es hora de volver al trabajo")
                    self.pomodoro_phase = "work"
                    self.pomodoro_time_left = 25 * 60  # 25 minutos de trabajo
                    self.phase_label.config(text="Trabajo", fg=COLOR_PALETTE["work"])
                    self.pomodoro_label.config(fg=COLOR_PALETTE["work"])
                
                self.update_pomodoro()

    def load_subjects_into_combobox(self):
        """Carga las materias del usuario en el combobox."""
        subjects = get_subjects(self.current_user_id)
        self.subject_map = {s['name']: s for s in subjects}
        self.materia_combobox['values'] = list(self.subject_map.keys())

    def registrar_sesion_estudio(self):
        materia = self.materia_combobox.get()
        duracion_str = self.duracion_entry.get()
        notas = self.notas_entry.get("1.0", tk.END).strip()

        if not materia or not duracion_str:
            messagebox.showerror("Error", "La materia y la duración son obligatorias.")
            return
        
        try:
            duracion = int(duracion_str)
            nueva_sesion = Estudio(self.current_user_id, materia, duracion, notas)
            self.estudio_repo.save(nueva_sesion)
            messagebox.showinfo("Éxito", "Sesión de estudio registrada.")
            self.refresh_data()
            # Limpiar campos
            self.duracion_entry.delete(0, tk.END)
            self.notas_entry.delete("1.0", tk.END)
        except ValueError:
            messagebox.showerror("Error", "La duración debe ser un número entero.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la sesión: {e}")

    def load_recent_sessions(self):
        """Carga las 5 sesiones de estudio más recientes."""
        for i in self.sessions_tree.get_children():
            self.sessions_tree.delete(i)
        
        sesiones = self.estudio_repo.find({"usuario_id": self.current_user_id})
        # Ordenar y limitar a 5
        for sesion in sorted(sesiones, key=lambda s: s.fecha_hora, reverse=True)[:5]:
            self.sessions_tree.insert("", "end", values=(
                sesion.materia,
                sesion.duracion_minutos,
                sesion.fecha_hora.strftime("%Y-%m-%d %H:%M")
            ))

    def load_goals_summary(self):
        """Muestra el progreso de las metas activas."""
        for widget in self.goals_frame.winfo_children():
            widget.destroy()

        metas = self.meta_repo.find({"usuario_id": self.current_user_id, "completada": False})
        if not metas:
            tk.Label(self.goals_frame, text="No tienes metas activas.", 
                    bg=COLOR_PALETTE["widget_bg"]).pack()
            return

        for meta in metas:
            if hasattr(meta, 'fecha_fin') and meta.fecha_fin and datetime.now() > meta.fecha_fin: 
                continue  # Omitir metas vencidas
            
            sesiones = self.estudio_repo.find({
                "usuario_id": self.current_user_id, 
                "materia": meta.materia,
                "fecha_hora": {"$gte": meta.fecha_inicio, "$lt": meta.fecha_fin}
            })
            minutos_logrados = sum(s.duracion_minutos for s in sesiones)
            progreso = (minutos_logrados / meta.minutos_objetivo) * 100 if meta.minutos_objetivo > 0 else 0
            
            # Manejar enum/string para el periodo
            periodo_str = meta.periodo.value if hasattr(meta.periodo, 'value') else meta.periodo
            
            tk.Label(self.goals_frame, text=f"{meta.materia} ({periodo_str})", 
                    bg=COLOR_PALETTE["widget_bg"]).pack(anchor="w")
            progress_bar = ttk.Progressbar(self.goals_frame, orient="horizontal", 
                                          length=200, mode="determinate", value=progreso)
            progress_bar.pack(fill="x", pady=2)
            tk.Label(self.goals_frame, text=f"{minutos_logrados} / {meta.minutos_objetivo} min", 
                    font=("Helvetica", 8), bg=COLOR_PALETTE["widget_bg"]).pack(anchor="w", pady=(0, 5))

    def open_goal_manager(self):
        """Abre una ventana para gestionar las metas."""
        manager_win = tk.Toplevel(self)
        manager_win.title("Gestionar Metas")
        manager_win.geometry("600x500")
        manager_win.configure(bg=COLOR_PALETTE["bg"])
        manager_win.transient(self)
        manager_win.grab_set()

        # --- Frame para añadir nueva meta ---
        add_frame = tk.LabelFrame(manager_win, text="Nueva Meta", bg=COLOR_PALETTE["bg"], padx=10, pady=10)
        add_frame.pack(fill="x", padx=10, pady=10)
        add_frame.grid_columnconfigure(1, weight=1)

        tk.Label(add_frame, text="Materia:", bg=COLOR_PALETTE["bg"], fg="white").grid(row=0, column=0, sticky="w", pady=2, padx=5)
        materia_combobox = ttk.Combobox(add_frame, state="readonly")
        materia_combobox.grid(row=0, column=1, sticky="ew", pady=2, padx=5)
        subjects = get_subjects(self.current_user_id)
        materia_combobox['values'] = [s['name'] for s in subjects]

        tk.Label(add_frame, text="Minutos Objetivo:", bg=COLOR_PALETTE["bg"], fg="white").grid(row=1, column=0, sticky="w", pady=2, padx=5)
        minutos_entry = tk.Entry(add_frame)
        minutos_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=5)

        tk.Label(add_frame, text="Periodo:", bg=COLOR_PALETTE["bg"], fg="white").grid(row=2, column=0, sticky="w", pady=2, padx=5)
        periodo_combobox = ttk.Combobox(add_frame, state="readonly", values=[p.value for p in PeriodoMeta])
        periodo_combobox.grid(row=2, column=1, sticky="ew", pady=2, padx=5)
        if periodo_combobox['values']:
            periodo_combobox.set(PeriodoMeta.SEMANAL.value)

        # --- Lista de metas existentes ---
        list_frame = tk.LabelFrame(manager_win, text="Mis Metas", bg=COLOR_PALETTE["bg"], padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        metas_tree = ttk.Treeview(list_frame, columns=("materia", "objetivo", "periodo", "estado"), show="headings")
        metas_tree.heading("materia", text="Materia")
        metas_tree.heading("objetivo", text="Objetivo (min)")
        metas_tree.heading("periodo", text="Periodo")
        metas_tree.heading("estado", text="Estado")
        metas_tree.column("materia", width=150)
        metas_tree.column("objetivo", width=100)
        metas_tree.column("periodo", width=100)
        metas_tree.column("estado", width=100)
        metas_tree.pack(fill="both", expand=True)

        def populate_goals_list():
            for i in metas_tree.get_children():
                metas_tree.delete(i)
            
            all_metas = self.meta_repo.find({"usuario_id": self.current_user_id})
            for meta in sorted(all_metas, key=lambda m: m.fecha_inicio, reverse=True):
                estado = "Completada" if meta.completada else "Activa"
                if not meta.completada and datetime.now() > meta.fecha_fin:
                    estado = "Vencida"
                
                # Manejar enum/string para el periodo
                periodo_str = meta.periodo.value if hasattr(meta.periodo, 'value') else meta.periodo
                
                metas_tree.insert("", "end", values=(
                    meta.materia,
                    meta.minutos_objetivo,
                    periodo_str,
                    estado
                ), iid=str(meta._id))
            
            self.refresh_data()

        def add_new_goal_action():
            materia = materia_combobox.get()
            minutos_str = minutos_entry.get()
            periodo_str = periodo_combobox.get()

            if not all([materia, minutos_str, periodo_str]):
                messagebox.showwarning("Datos incompletos", "Todos los campos son necesarios.", parent=manager_win)
                return
            
            try:
                minutos = int(minutos_str)
                periodo = PeriodoMeta(periodo_str)
                nueva_meta = Meta(self.current_user_id, materia, minutos, periodo)
                self.meta_repo.save(nueva_meta)
                
                materia_combobox.set('')
                minutos_entry.delete(0, tk.END)
                populate_goals_list()
            except ValueError:
                messagebox.showerror("Error", "Los minutos deben ser un número entero.", parent=manager_win)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar la meta: {e}", parent=manager_win)

        def delete_selected_goal():
            selected_item_id = metas_tree.focus()
            if not selected_item_id:
                messagebox.showwarning("Sin selección", "Por favor, selecciona una meta para eliminar.", parent=manager_win)
                return
            
            if messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar esta meta?", parent=manager_win):
                self.meta_repo.delete_by_id(ObjectId(selected_item_id))
                populate_goals_list()

        add_btn = tk.Button(add_frame, text="Añadir Meta", command=add_new_goal_action, 
                           bg=COLOR_PALETTE["accent"], fg="white", relief="flat")
        add_btn.grid(row=3, column=1, sticky="e", pady=10)

        del_btn = tk.Button(list_frame, text="Eliminar Seleccionada", command=delete_selected_goal, 
                           bg=COLOR_PALETTE["accent"], fg="white", relief="flat")
        del_btn.pack(pady=5, anchor="e")

        populate_goals_list()

    def open_subject_manager(self):
        """Abre una ventana para gestionar las materias."""
        manager_win = tk.Toplevel(self)
        manager_win.title("Gestionar Materias")
        manager_win.geometry("400x400")
        manager_win.configure(bg=COLOR_PALETTE["bg"])
        manager_win.transient(self)
        manager_win.grab_set()

        # Frame para añadir nueva materia
        add_frame = tk.Frame(manager_win, bg=COLOR_PALETTE["bg"], pady=10)
        add_frame.pack(fill="x", padx=10)
        
        tk.Label(add_frame, text="Nombre:", bg=COLOR_PALETTE["bg"], fg="white").pack(side="left")
        name_entry = tk.Entry(add_frame)
        name_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        color_val = tk.StringVar(value="#DA6C6C")
        def choose_color():
            color_code = colorchooser.askcolor(title="Elige un color")
            if color_code[1]:
                color_val.set(color_code[1])
                color_btn.config(bg=color_code[1])

        color_btn = tk.Button(add_frame, text="Color", command=choose_color, 
                             bg=color_val.get(), relief="flat", fg="white")
        color_btn.pack(side="left", padx=5)

        def add_new_subject_action():
            name = name_entry.get()
            color = color_val.get()
            if name and color:
                add_subject(self.current_user_id, name, color)
                name_entry.delete(0, tk.END)
                populate_list()
                self.load_subjects_into_combobox() # Actualizar combobox en dashboard
            else:
                messagebox.showwarning("Datos incompletos", "El nombre y el color son necesarios.")

        add_btn = tk.Button(add_frame, text="Añadir", command=add_new_subject_action, 
                           bg=COLOR_PALETTE["accent"], fg="white", relief="flat")
        add_btn.pack(side="left", padx=5)

        # Lista de materias existentes
        list_frame = tk.Frame(manager_win, bg=COLOR_PALETTE["bg"])
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        def populate_list():
            for widget in list_frame.winfo_children():
                widget.destroy()
            
            subjects = get_subjects(self.current_user_id)
            for subject in subjects:
                item_frame = tk.Frame(list_frame, bg=COLOR_PALETTE["widget_bg"], pady=5)
                item_frame.pack(fill="x", pady=2)
                
                color = subject.get('color', "#CCCCCC")  # Color por defecto
                
                color_label = tk.Label(item_frame, text="  ", bg=color, width=3)
                color_label.pack(side="left", padx=10)
                
                tk.Label(item_frame, text=subject.get('name', 'Nombre no encontrado'), 
                        bg=COLOR_PALETTE["widget_bg"]).pack(side="left", expand=True, fill="x", anchor="w")
                
                def delete_action(s_id=subject.get('_id')):
                    if messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar esta materia?"):
                        delete_subject(s_id)
                        populate_list()
                        self.load_subjects_into_combobox()

                del_btn = tk.Button(item_frame, text="Eliminar", command=delete_action, 
                                   bg=COLOR_PALETTE["accent"], fg="white", relief="flat")
                del_btn.pack(side="right", padx=10)

        populate_list()