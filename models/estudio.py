from datetime import datetime
from typing import Dict, Any, Optional

class Estudio:
    """Clase que representa una sesión de estudio."""
    
    def __init__(self, usuario_id: str, materia: str, duracion_minutos: int, 
                 notas: Optional[str] = None):
        self.__id = None  # Será asignado por MongoDB
        self.__usuario_id = usuario_id
        self.__materia = materia
        self.__duracion_minutos = duracion_minutos
        self.__fecha_hora = datetime.now()
        self.__notas = notas
        
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
    def duracion_minutos(self) -> int:
        return self.__duracion_minutos
    
    @property
    def fecha_hora(self) -> datetime:
        return self.__fecha_hora
    
    @property
    def notas(self) -> Optional[str]:
        return self.__notas
    
    @notas.setter
    def notas(self, value: Optional[str]) -> None:
        self.__notas = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario para almacenamiento en MongoDB."""
        return {
            "usuario_id": self.__usuario_id,
            "materia": self.__materia,
            "duracion_minutos": self.__duracion_minutos,
            "fecha_hora": self.__fecha_hora,
            "notas": self.__notas
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Estudio':
        """Crea una instancia de Estudio desde un diccionario."""
        estudio = cls(
            usuario_id=data["usuario_id"],
            materia=data["materia"],
            duracion_minutos=data["duracion_minutos"],
            notas=data.get("notas")
        )
        
        # Establecer otros atributos
        if "_id" in data:
            estudio.id = str(data["_id"])
            
        estudio.__fecha_hora = data.get("fecha_hora", datetime.now())
        
        return estudio