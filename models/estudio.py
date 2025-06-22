from datetime import datetime
from typing import Dict, Any, Optional

class Estudio:
    """Clase que representa una sesión de estudio."""
    
    def __init__(self, usuario_id=None, materia=None, duracion_minutos=0, notas=None, fecha_hora=None):
        self._id = None
        self.usuario_id = usuario_id
        self.materia = materia
        self.duracion_minutos = duracion_minutos
        self.notas = notas
        self.fecha_hora = fecha_hora or datetime.now()
    
    @classmethod
    def from_dict(cls, data):
        instance = cls()
        for key, value in data.items():
            setattr(instance, key, value)
        return instance
    
    def to_dict(self):
        return {
            "usuario_id": self.usuario_id,
            "materia": self.materia,
            "duracion_minutos": self.duracion_minutos,
            "notas": self.notas,
            "fecha_hora": self.fecha_hora
        }