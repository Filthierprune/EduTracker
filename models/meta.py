from datetime import datetime, timedelta
from enum import Enum

class PeriodoMeta(Enum):
    DIARIO = "Diario"
    SEMANAL = "Semanal"
    MENSUAL = "Mensual"

class Meta:
    def __init__(self, usuario_id=None, materia=None, minutos_objetivo=0, periodo=PeriodoMeta.SEMANAL, fecha_inicio=None):
        self._id = None
        self.usuario_id = usuario_id
        self.materia = materia
        self.minutos_objetivo = minutos_objetivo
        self.periodo = periodo
        self.fecha_inicio = fecha_inicio or datetime.now()
        self.completada = False
        
        # Calcular fecha fin según el periodo
        if periodo == PeriodoMeta.DIARIO:
            self.fecha_fin = self.fecha_inicio + timedelta(days=1)
        elif periodo == PeriodoMeta.SEMANAL:
            self.fecha_fin = self.fecha_inicio + timedelta(weeks=1)
        else:  # MENSUAL
            self.fecha_fin = self.fecha_inicio + timedelta(days=30)
    
    @classmethod
    def from_dict(cls, data):
        instance = cls()
        for key, value in data.items():
            if key == 'periodo' and isinstance(value, str):
                setattr(instance, key, PeriodoMeta(value))
            else:
                setattr(instance, key, value)
        return instance
    
    def to_dict(self):
        return {
            "usuario_id": self.usuario_id,
            "materia": self.materia,
            "minutos_objetivo": self.minutos_objetivo,
            "periodo": self.periodo.value if isinstance(self.periodo, PeriodoMeta) else self.periodo,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "completada": self.completada
        }