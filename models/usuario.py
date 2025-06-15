from datetime import datetime
from typing import List, Dict, Any, Optional

class Usuario:
    """Clase que representa a un usuario del sistema de monitoreo de estudios."""
    
    def __init__(self, nombre: str, email: str, password: str):
        self.__id = None  # Será asignado por MongoDB
        self.__nombre = nombre
        self.__email = email
        self.__password = password  # En una aplicación real, debería estar hasheado
        self.__fecha_registro = datetime.now()
        self.__materias = []
        
    @property
    def id(self) -> Optional[str]:
        return self.__id
        
    @id.setter
    def id(self, value: str) -> None:
        if self.__id is None:  # Solo permitir establecer el ID una vez
            self.__id = value
            
    @property
    def nombre(self) -> str:
        return self.__nombre
        
    @nombre.setter
    def nombre(self, value: str) -> None:
        if value and isinstance(value, str):
            self.__nombre = value
            
    @property
    def email(self) -> str:
        return self.__email
    
    @property
    def materias(self) -> List[str]:
        return self.__materias.copy()  # Devolver una copia para evitar modificaciones directas
        
    def agregar_materia(self, materia: str) -> None:
        """Agrega una nueva materia al usuario si no existe."""
        if materia and materia not in self.__materias:
            self.__materias.append(materia)
            
    def eliminar_materia(self, materia: str) -> bool:
        """Elimina una materia de la lista. Retorna True si se eliminó correctamente."""
        if materia in self.__materias:
            self.__materias.remove(materia)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario para almacenamiento en MongoDB."""
        return {
            "nombre": self.__nombre,
            "email": self.__email,
            "password": self.__password,  # En una app real, ya estaría hasheado
            "fecha_registro": self.__fecha_registro,
            "materias": self.__materias
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Usuario':
        """Crea una instancia de Usuario desde un diccionario."""
        usuario = cls(
            nombre=data["nombre"],
            email=data["email"],
            password=data["password"]
        )
        
        # Establecer otros atributos
        if "_id" in data:
            usuario.id = str(data["_id"])
            
        usuario.__fecha_registro = data.get("fecha_registro", datetime.now())
        usuario.__materias = data.get("materias", [])
        
        return usuario