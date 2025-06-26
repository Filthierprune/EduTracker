# utils/chart.py
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from datetime import datetime, timedelta
from database import get_subjects

class ProgressChart:
    def __init__(self, parent, user_id):
        self.parent = parent
        self.user_id = user_id
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = None
        
    def create_chart(self, estudio_repo):
        """Crea la gráfica de progreso semanal."""
        # Limpiar gráfica anterior
        self.ax.clear()
        
        # Calcular fecha de inicio (lunes de esta semana)
        today = datetime.now()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        
        # Obtener materias con sus colores
        subjects = get_subjects(self.user_id)
        subject_colors = {s['name']: s.get('color', '#888888') for s in subjects}
        
        # Obtener sesiones de esta semana
        sesiones = estudio_repo.find({
            "usuario_id": self.user_id,
            "fecha_hora": {"$gte": start_date, "$lte": end_date}
        })
        
        # Agrupar por materia
        minutos_por_materia = {}
        for sesion in sesiones:
            materia = sesion.materia
            minutos_por_materia[materia] = minutos_por_materia.get(materia, 0) + sesion.duracion_minutos
        
        # Preparar datos para la gráfica
        materias = list(minutos_por_materia.keys())
        minutos = [minutos_por_materia[m] for m in materias]
        colores = [subject_colors.get(m, '#888888') for m in materias]
        
        # Crear gráfica de barras
        bars = self.ax.bar(materias, minutos, color=colores)
        self.ax.set_title('Progreso Semanal por Materia')
        self.ax.set_ylabel('Minutos')
        self.ax.tick_params(axis='x', rotation=45)
        
        # Añadir etiquetas con los valores
        for bar in bars:
            height = bar.get_height()
            self.ax.annotate(f'{height}',
                             xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3),
                             textcoords="offset points",
                             ha='center', va='bottom')
        
        # Integrar en Tkinter
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)