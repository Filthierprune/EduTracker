import os
from dotenv import load_dotenv
from database.mongo_client import MongoDBClient
from ui.cli import CLI

def main():
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener cadena de conexión a MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("DB_NAME", "edutracker")
    
    print("Iniciando EduTracker...")
    print("Conectando a la base de datos...")
    
    try:
        # Inicializar cliente de MongoDB
        db_client = MongoDBClient(mongo_uri, db_name)
        
        # Iniciar interfaz CLI
        cli = CLI(db_client)
        cli.mostrar_menu_principal()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {str(e)}")
        input("Presione Enter para salir...")

if __name__ == "__main__":
    main()