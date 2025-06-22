import pymongo
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno desde configuracion.env
load_dotenv("configuracion.env")

# --- Configuración de la Conexión ---
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# --- Cliente de MongoDB ---
client = None
db = None

def connect_to_db():
    """
    Establece la conexión con la base de datos MongoDB.
    """
    global client, db
    try:
        # Usamos timeout para evitar que la aplicación se congele si la base de datos no responde.
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Forzamos una conexión para verificar que el servidor está disponible.
        client.admin.command('ping')
        print("Conexión a MongoDB exitosa.")
        db = client[DB_NAME]
        return db
    except ConnectionFailure as e:
        print(f"Error de conexión a MongoDB. Asegúrate de que el servidor esté corriendo. Error: {e}")
        client = None
        db = None
        return None

# --- Funciones de Usuario (Aún no conectadas a la GUI) ---
def register_user(username, password, email):
    """
    Registra un nuevo usuario en la base de datos.
    PENDIENTE: Añadir hashing de contraseña antes de guardar.
    """
    if db is None:
        print("La conexión a la base de datos no está establecida.")
        return None
    
    users_collection = db.users
    # TODO: Verificar si el usuario o el email ya existen.
    user_data = {
        "username": username,
        "password": password, # ¡ADVERTENCIA! Nunca guardes contraseñas en texto plano.
        "email": email,
        "created_at": datetime.now()
    }
    result = users_collection.insert_one(user_data)