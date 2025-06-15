from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from enum import Enum

class PeriodoMeta(Enum):
    DIARIO = "diario"
    SEMANAL = "semanal"
    MENSUAL = "mensual"

class Meta:
    """Clase que representa una meta de estudio."""
    
    def __init__(self, usuario_id: str, materia: str, minutos_objetivo: int, 
                 periodo: PeriodoMeta, fecha_inicio: Optional[datetime] = None):
        self.__id = None  # Será asignado por MongoDB
        self.__usuario_id = usuario_id
        self.__materia = materia
        self.__minutos_objetivo = minutos_objetivo
        self.__periodo = periodo
        self.__fecha_inicio = fecha_inicio or datetime.now()
        self.__completada = False
        
    @property
    def id(self) -> Optional[str]:
        return self.__id
        
    @id.setter
    def id(self, value: str) -> None:
        if self.__id is None:
            self.__id = value
    
    @property
    def usuario_id(self) -> str:
        return self.__usuario_id
    
    @property
    def materia(self) -> str:
        return self.__materia
    
    @property
    def minutos_objetivo(self) -> int:
        return self.__minutos_objetivo
    
    @property
    def periodo(self) -> PeriodoMeta:
        return self.__periodo
    
    @property
    def fecha_inicio(self) -> datetime:
        return self.__fecha_inicio
    
    @property
    def fecha_fin(self) -> datetime:
        """Calcula la fecha de finalización basada en el periodo."""
        if self.__periodo == PeriodoMeta.DIARIO:
            return self.__fecha_inicio + timedelta(days=1)
        elif self.__periodo == PeriodoMeta.SEMANAL:
            return self.__fecha_inicio + timedelta(weeks=1)
        elif self.__periodo == PeriodoMeta.MENSUAL:
            # Aproximación simple para un mes (30 días)
            return self.__fecha_inicio + timedelta(days=30)
    
    @property
    def completada(self) -> bool:
        return self.__completada
    
    @completada.setter
    def completada(self, value: bool) -> None:
        self.__completada = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario para almacenamiento en MongoDB."""
        return {
            "usuario_id": self.__usuario_id,
            "materia": self.__materia,
            "minutos_objetivo": self.__minutos_objetivo,
            "periodo": self.__periodo.value,
            "fecha_inicio": self.__fecha_inicio,
            "completada": self.__completada
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Meta':
        """Crea una instancia de Meta desde un diccionario."""
        meta = cls(
            usuario_id=data["usuario_id"],
            materia=data["materia"],
            minutos_objetivo=data["minutos_objetivo"],
            periodo=PeriodoMeta(data["periodo"]),
            fecha_inicio=data.get("fecha_inicio")
        )
        
        # Establecer otros atributos
        if "_id" in data:
            meta.id = str(data["_id"])
            
        meta.__completada = data.get("completada", False)
        
        return meta