from pymongo import MongoClient
import certifi
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
        ca = certifi.where()
        try:
            self.client = MongoClient(connection_string, tlsCAFile=ca)
            self.client.admin.command('ping')
            print("Conexión a MongoDB Atlas exitosa usando MongoDBClient!")
        except Exception as e:
            print(f"Error al conectar a MongoDB en MongoDBClient: {e}")
            self.client = None
        
        if self.client is not None: # Comprobar si el cliente se inicializó
            self.db = self.client[db_name]
        else:
            self.db = None
    
    def insert_one(self, collection: str, data: Dict[str, Any]) -> str:
        """
        Inserta un documento en la colección especificada.
        
        Args:
            collection: Nombre de la colección
            data: Diccionario con los datos a insertar
            
        Returns:
            ID del documento insertado
        """
        if self.db is None: # <--- MODIFICADO
            raise ConnectionError("No hay conexión a la base de datos.")
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
        if self.db is None: # <--- MODIFICADO
            raise ConnectionError("No hay conexión a la base de datos.")
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
        # Esta función llama a find_one, que ya tiene la verificación
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
        if self.db is None: # <--- MODIFICADO
            raise ConnectionError("No hay conexión a la base de datos.")
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
        if self.db is None: # <--- MODIFICADO
            raise ConnectionError("No hay conexión a la base de datos.")
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
        if self.db is None: # <--- MODIFICADO
            raise ConnectionError("No hay conexión a la base de datos.")
        result = self.db[collection].delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0


class MongoRepository:
    """Repositorio genérico para manejar operaciones CRUD en MongoDB."""
    
    def __init__(self, db_client, collection_name, model_class):
        """
        Inicializa el repositorio.
        
        Args:
            db_client: Cliente de MongoDB
            collection_name: Nombre de la colección
            model_class: Clase del modelo
        """
        self.db_client = db_client
        self.collection_name = collection_name
        self.model_class = model_class
        # Obtenemos la colección directamente del cliente de base de datos
        self.collection = db_client[collection_name] if db_client is not None else None
        
    def find(self, query=None):
        """Busca documentos que coincidan con la consulta"""
        if self.collection is None:
            return []
            
        results = []
        # Usamos el método find() estándar de PyMongo
        for doc in self.collection.find(query or {}):
            # Asumimos que el modelo tiene un método from_dict
            if hasattr(self.model_class, 'from_dict'):
                results.append(self.model_class.from_dict(doc))
            else:
                # Fallback en caso de que no exista el método
                instance = self.model_class()
                for key, value in doc.items():
                    setattr(instance, key, value)
                results.append(instance)
        return results
        
    def save(self, model):
        """Guarda un modelo en la colección"""
        if self.collection is None:
            raise ConnectionError("No hay conexión a la base de datos")
            
        # Convertir el modelo a diccionario
        if hasattr(model, 'to_dict'):
            data = model.to_dict()
        else:
            # Fallback para convertir el objeto a diccionario
            data = {key: value for key, value in model.__dict__.items() 
                   if not key.startswith('_')}
        
        if hasattr(model, '_id') and getattr(model, '_id', None):
            # Actualizar documento existente
            self.collection.update_one({"_id": model._id}, {"$set": data})
        else:
            # Insertar nuevo documento
            result = self.collection.insert_one(data)
            model._id = result.inserted_id
            
        return model

