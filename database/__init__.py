import pymongo
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv
from datetime import datetime
import bcrypt

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

# --- Funciones de Autenticación de Usuario ---
def register_user(username, password, email):
    """Registra un nuevo usuario con contraseña hasheada."""
    if db is None:
        return False, "La conexión a la base de datos no está establecida."
    
    users_collection = db.users
    
    # Verificar si el usuario o el email ya existen
    if users_collection.find_one({"username": username}):
        return False, "El nombre de usuario ya existe."
    if users_collection.find_one({"email": email}):
        return False, "El correo electrónico ya está en uso."

    # Hashear la contraseña
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    user_data = {
        "username": username,
        "password": hashed_password,
        "email": email,
        "created_at": datetime.now()
    }
    users_collection.insert_one(user_data)
    return True, "Usuario registrado con éxito."

def check_user(username, password):
    """Verifica las credenciales de un usuario comparando la contraseña hasheada."""
    if db is None:
        print("La conexión a la base de datos no está establecida.")
        return None

    users_collection = db.users
    user = users_collection.find_one({"username": username})
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        print(f"Usuario '{username}' autenticado correctamente.")
        return user
    else:
        print("Credenciales inválidas.")
        return None

# --- Inicializar Conexión al Cargar el Módulo ---
connect_to_db()