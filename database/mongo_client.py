from pymongo import MongoClient
from typing import Dict, List, Any, Optional, TypeVar, Generic, Type
from bson.objectid import ObjectId

T = TypeVar('T')

class MongoDBClient:
    """Cliente para interactuar con MongoDB."""
    
    def __init__(self, connection_string: str, db_name: str):
        """
        Inicializa la conexión a MongoDB.
        
        Args:
            connection_string: URL de conexión a MongoDB
            db_name: Nombre de la base de datos
        """
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
    
    def insert_one(self, collection: str, data: Dict[str, Any]) -> str:
        """
        Inserta un documento en la colección especificada.
        
        Args:
            collection: Nombre de la colección
            data: Diccionario con los datos a insertar
            
        Returns:
            ID del documento insertado
        """
        result = self.db[collection].insert_one(data)
        return str(result.inserted_id)
    
    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Busca un documento en la colección especificada.
        
        Args:
            collection: Nombre de la colección
            query: Consulta para filtrar documentos
            
        Returns:
            Documento encontrado o None si no existe
        """
        result = self.db[collection].find_one(query)
        return result
    
    def find_by_id(self, collection: str, id: str) -> Optional[Dict[str, Any]]:
        """
        Busca un documento por su ID.
        
        Args:
            collection: Nombre de la colección
            id: ID del documento
            
        Returns:
            Documento encontrado o None si no existe
        """
        return self.find_one(collection, {"_id": ObjectId(id)})
    
    def find_many(self, collection: str, query: Dict[str, Any], 
                  sort: Optional[List[tuple]] = None, 
                  limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Busca múltiples documentos en la colección.
        
        Args:
            collection: Nombre de la colección
            query: Consulta para filtrar documentos
            sort: Lista de tuplas (campo, dirección) para ordenar resultados
            limit: Número máximo de resultados
            
        Returns:
            Lista de documentos encontrados
        """
        cursor = self.db[collection].find(query)
        
        if sort:
            cursor = cursor.sort(sort)
            
        if limit:
            cursor = cursor.limit(limit)
            
        return list(cursor)
    
    def update_one(self, collection: str, id: str, 
                   data: Dict[str, Any]) -> bool:
        """
        Actualiza un documento por su ID.
        
        Args:
            collection: Nombre de la colección
            id: ID del documento
            data: Datos para actualizar
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        result = self.db[collection].update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )
        return result.modified_count > 0
    
    def delete_one(self, collection: str, id: str) -> bool:
        """
        Elimina un documento por su ID.
        
        Args:
            collection: Nombre de la colección
            id: ID del documento
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        result = self.db[collection].delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0


class MongoRepository(Generic[T]):
    """Repositorio genérico para manejar operaciones CRUD en MongoDB."""
    
    def __init__(self, db_client: MongoDBClient, collection: str, model_class: Type[T]):
        """
        Inicializa el repositorio.
        
        Args:
            db_client: Cliente de MongoDB
            collection: Nombre de la colección
            model_class: Clase del modelo
        """
        self.db_client = db_client
        self.collection = collection
        self.model_class = model_class
    
    def save(self, entity: T) -> str:
        """
        Guarda una entidad en la base de datos.
        
        Args:
            entity: Entidad a guardar
            
        Returns:
            ID de la entidad guardada
        """
        data = entity.to_dict()
        entity_id = self.db_client.insert_one(self.collection, data)
        return entity_id
    
    def find_by_id(self, id: str) -> Optional[T]:
        """
        Busca una entidad por su ID.
        
        Args:
            id: ID de la entidad
            
        Returns:
            Entidad encontrada o None si no existe
        """
        data = self.db_client.find_by_id(self.collection, id)
        if data:
            return self.model_class.from_dict(data)
        return None
    
    def find(self, query: Dict[str, Any]) -> List[T]:
        """
        Busca entidades según una consulta.
        
        Args:
            query: Consulta para filtrar entidades
            
        Returns:
            Lista de entidades encontradas
        """
        data_list = self.db_client.find_many(self.collection, query)
        return [self.model_class.from_dict(data) for data in data_list]
    
    def update(self, entity: T) -> bool:
        """
        Actualiza una entidad.
        
        Args:
            entity: Entidad a actualizar
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        if not entity.id:
            return False
        
        data = entity.to_dict()
        return self.db_client.update_one(self.collection, entity.id, data)
    
    def delete(self, id: str) -> bool:
        """
        Elimina una entidad por su ID.
        
        Args:
            id: ID de la entidad
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        return self.db_client.delete_one(self.collection, id)