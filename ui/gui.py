import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
from datetime import datetime
from database.mongo_client import MongoRepository
from models.estudio import Estudio
from models.meta import Meta, PeriodoMeta
from database import get_subjects, add_subject, delete_subject
from bson.objectid import ObjectId

# --- Colores del diseño ---
COLOR_PALETTE = {
    "bg": "#EAEBD0",
    "primary": "#DB7676",
    "accent": "#AF3E3E",
    "text": "#333333",
    "widget_bg": "#FDFDFD"
}

class MainDashboardFrame(tk.Frame):
    """Frame principal rediseñado que contiene el dashboard de la aplicación."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_PALETTE["bg"])
        self.controller = controller
        self.db_client = controller.db_client
        self.current_user_id = None

    def set_user(self, user_data):
        """Configura el usuario actual y carga la interfaz del dashboard."""
        self.current_user_id = user_data["username"]
        self.controller.title(f"EduTracker - Usuario: {self.current_user_id}")
        
        for widget in self.winfo_children():
            widget.destroy()

        self.estudio_repo = MongoRepository(self.db_client, 'sesiones_estudio', Estudio)
        self.meta_repo = MongoRepository(self.db_client, 'metas', Meta)

        self.create_dashboard_layout()
        self.refresh_data()

    def refresh_data(self):
        """Recarga todos los datos del dashboard."""
        self.load_recent_sessions()
        self.load_goals_summary()
        # Aquí se llamarán a las futuras funciones de carga de datos

    def create_dashboard_layout(self):
        # --- Header ---
        header_frame = tk.Frame(self, bg=COLOR_PALETTE["bg"])
        header_frame.pack(fill="x", pady=10, padx=20)
        
        tk.Label(header_frame, text=f"Bienvenido, {self.current_user_id}", font=("Helvetica", 16, "bold"), bg=COLOR_PALETTE["bg"]).pack(side="left", padx=10)
        
        logout_btn = tk.Button(header_frame, text="Cerrar Sesión", bg=COLOR_PALETTE["accent"], fg="white", relief="flat", command=lambda: self.controller.show_frame("LoginFrame"))
        logout_btn.pack(side="right", padx=5)
        
        goals_btn = tk.Button(header_frame, text="Gestionar Metas", bg=COLOR_PALETTE["primary"], fg="white", relief="flat", command=self.open_goal_manager)
        goals_btn.pack(side="right", padx=5)
        
        subjects_btn = tk.Button(header_frame, text="Gestionar Materias", bg=COLOR_PALETTE["primary"], fg="white", relief="flat", command=self.open_subject_manager)
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
        # Placeholder para Pomodoro
        pomodoro_frame = tk.LabelFrame(left_panel, text="Temporizador Pomodoro", padx=10, pady=10, bg=COLOR_PALETTE["widget_bg"])
        pomodoro_frame.pack(fill="x", pady=10)
        tk.Label(pomodoro_frame, text="Próximamente...", bg=COLOR_PALETTE["widget_bg"]).pack()

        # --- Panel Derecho (Información) ---
        right_panel = tk.Frame(main_container, bg=COLOR_PALETTE["bg"])
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Resumen de Metas
        self.goals_frame = tk.LabelFrame(right_panel, text="Resumen de Metas", padx=10, pady=10, bg=COLOR_PALETTE["widget_bg"])
        self.goals_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Historial de Sesiones
        sessions_frame = tk.LabelFrame(right_panel, text="Historial de Sesiones Recientes", padx=10, pady=10, bg=COLOR_PALETTE["widget_bg"])
        sessions_frame.grid(row=1, column=0, sticky="nsew")
        
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=("materia", "duracion", "fecha"), show="headings")
        self.sessions_tree.heading("materia", text="Materia")
        self.sessions_tree.heading("duracion", text="Duración (min)")
        self.sessions_tree.heading("fecha", text="Fecha")
        self.sessions_tree.pack(fill="both", expand=True)

    def create_study_session_widget(self, parent):
        """Crea el widget para registrar una nueva sesión de estudio."""
        widget_frame = tk.LabelFrame(parent, text="Nueva Sesión de Estudio", padx=10, pady=10, bg=COLOR_PALETTE["widget_bg"])
        widget_frame.pack(fill="x")

        ttk.Label(widget_frame, text="Materia:", background=COLOR_PALETTE["widget_bg"]).grid(row=0, column=0, sticky="w", pady=2)
        self.materia_combobox = ttk.Combobox(widget_frame, state="readonly")
        self.materia_combobox.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(widget_frame, text="Duración (min):", background=COLOR_PALETTE["widget_bg"]).grid(row=1, column=0, sticky="w", pady=2)
        self.duracion_entry = ttk.Entry(widget_frame)
        self.duracion_entry.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(widget_frame, text="Notas:", background=COLOR_PALETTE["widget_bg"]).grid(row=2, column=0, sticky="w", pady=2)
        self.notas_entry = tk.Text(widget_frame, height=4, width=30)
        self.notas_entry.grid(row=2, column=1, sticky="ew", pady=2)

        save_btn = ttk.Button(widget_frame, text="Guardar Sesión", command=self.registrar_sesion_estudio)
        save_btn.grid(row=3, column=1, sticky="e", pady=10)
        
        self.load_subjects_into_combobox()

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
            self.materia_combobox.set('')
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
            tk.Label(self.goals_frame, text="No tienes metas activas.", bg=COLOR_PALETTE["widget_bg"]).pack()
            return

        for meta in metas:
            if datetime.now() > meta.fecha_fin: continue # Omitir vencidas
            
            sesiones = self.estudio_repo.find({
                "usuario_id": self.current_user_id, "materia": meta.materia,
                "fecha_hora": {"$gte": meta.fecha_inicio, "$lt": meta.fecha_fin}
            })
            minutos_logrados = sum(s.duracion_minutos for s in sesiones)
            progreso = (minutos_logrados / meta.minutos_objetivo) * 100 if meta.minutos_objetivo > 0 else 100

            tk.Label(self.goals_frame, text=f"{meta.materia} ({meta.periodo.value})", bg=COLOR_PALETTE["widget_bg"]).pack(anchor="w")
            progress_bar = ttk.Progressbar(self.goals_frame, orient="horizontal", length=200, mode="determinate", value=progreso)
            progress_bar.pack(fill="x", pady=2)
            tk.Label(self.goals_frame, text=f"{minutos_logrados} / {meta.minutos_objetivo} min", font=("Helvetica", 8), bg=COLOR_PALETTE["widget_bg"]).pack(anchor="w", pady=(0, 5))

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

        tk.Label(add_frame, text="Materia:", bg=COLOR_PALETTE["bg"]).grid(row=0, column=0, sticky="w", pady=2, padx=5)
        materia_combobox = ttk.Combobox(add_frame, state="readonly")
        materia_combobox.grid(row=0, column=1, sticky="ew", pady=2)
        subjects = get_subjects(self.current_user_id)
        materia_combobox['values'] = [s['name'] for s in subjects]

        tk.Label(add_frame, text="Minutos Objetivo:", bg=COLOR_PALETTE["bg"]).grid(row=1, column=0, sticky="w", pady=2, padx=5)
        minutos_entry = tk.Entry(add_frame)
        minutos_entry.grid(row=1, column=1, sticky="ew", pady=2)

        tk.Label(add_frame, text="Periodo:", bg=COLOR_PALETTE["bg"]).grid(row=2, column=0, sticky="w", pady=2, padx=5)
        periodo_combobox = ttk.Combobox(add_frame, state="readonly", values=[p.value for p in PeriodoMeta])
        periodo_combobox.grid(row=2, column=1, sticky="ew", pady=2)
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
        metas_tree.pack(fill="both", expand=True)

        def populate_goals_list():
            for i in metas_tree.get_children():
                metas_tree.delete(i)
            
            all_metas = self.meta_repo.find({"usuario_id": self.current_user_id})
            for meta in sorted(all_metas, key=lambda m: m.fecha_inicio, reverse=True):
                estado = "Completada" if meta.completada else "Activa"
                if not meta.completada and datetime.now() > meta.fecha_fin:
                    estado = "Vencida"
                
                metas_tree.insert("", "end", values=(
                    meta.materia,
                    meta.minutos_objetivo,
                    meta.periodo.value if hasattr(meta.periodo, 'value') else meta.periodo,
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
                self.db_client.metas.delete_one({"_id": ObjectId(selected_item_id)})
                populate_goals_list()

        add_btn = tk.Button(add_frame, text="Añadir Meta", command=add_new_goal_action, bg=COLOR_PALETTE["accent"], fg="white", relief="flat")
        add_btn.grid(row=3, column=1, sticky="e", pady=10)

        del_btn = tk.Button(list_frame, text="Eliminar Seleccionada", command=delete_selected_goal, bg=COLOR_PALETTE["accent"], fg="white", relief="flat")
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
        
        tk.Label(add_frame, text="Nombre:", bg=COLOR_PALETTE["bg"]).pack(side="left")
        name_entry = tk.Entry(add_frame)
        name_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        color_val = tk.StringVar(value="#DA6C6C")
        def choose_color():
            color_code = colorchooser.askcolor(title="Elige un color")
            if color_code:
                color_val.set(color_code[1])
                color_btn.config(bg=color_code[1])

        color_btn = tk.Button(add_frame, text="Color", command=choose_color, bg=color_val.get(), relief="flat", fg="white")
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

        add_btn = tk.Button(add_frame, text="Añadir", command=add_new_subject_action, bg=COLOR_PALETTE["accent"], fg="white", relief="flat")
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
                
                # Usar .get() para obtener el color y proporcionar uno por defecto si no existe
                color = subject.get('color') or "#CCCCCC"  # Gris por defecto
                
                color_label = tk.Label(item_frame, text="  ", bg=color)
                color_label.pack(side="left", padx=10)
                
                tk.Label(item_frame, text=subject.get('name', 'Nombre no encontrado'), bg=COLOR_PALETTE["widget_bg"]).pack(side="left", expand=True, fill="x", anchor="w")
                
                def delete_action(s_id=subject.get('_id')):
                    if messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar esta materia?"):
                        delete_subject(s_id)
                        populate_list()
                        self.load_subjects_into_combobox()

                del_btn = tk.Button(item_frame, text="Eliminar", command=delete_action, bg=COLOR_PALETTE["accent"], fg="white", relief="flat")
                del_btn.pack(side="right", padx=10)

        populate_list()