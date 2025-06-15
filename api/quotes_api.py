import requests
from typing import Dict, List, Optional, Any
import random

class QuotesAPI:
    """Clase para interactuar con la API de ZenQuotes."""
    
    def __init__(self):
        self.base_url = "https://zenquotes.io/api"
    
    def get_random_quote(self) -> Optional[Dict[str, str]]:
        """
        Obtiene una frase motivacional aleatoria.
        
        Returns:
            Diccionario con la frase y el autor, o None si hay un error
        """
        try:
            response = requests.get(f"{self.base_url}/random")
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return {
                        "quote": data[0]["q"],
                        "author": data[0]["a"]
                    }
            return None
        except Exception as e:
            print(f"Error al obtener frase: {str(e)}")
            return None
    
    def get_daily_quote(self) -> Optional[Dict[str, str]]:
        """
        Obtiene la frase motivacional del día.
        
        Returns:
            Diccionario con la frase y el autor, o None si hay un error
        """
        try:
            response = requests.get(f"{self.base_url}/today")
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return {
                        "quote": data[0]["q"],
                        "author": data[0]["a"]
                    }
            return None
        except Exception as e:
            print(f"Error al obtener frase del día: {str(e)}")
            return None
    
    def get_quotes_by_topic(self, topic: str) -> List[Dict[str, str]]:
        """
        Obtiene frases relacionadas con un tema específico.
        
        Args:
            topic: Tema para filtrar frases
            
        Returns:
            Lista de diccionarios con frases y autores
        """
        # Nota: En la API gratuita de ZenQuotes no hay búsqueda por tema
        # Esta es una implementación simulada
        
        # Lista de frases relacionadas con el estudio
        study_quotes = [
            {"quote": "El estudio es la forja que da forma al carácter.", "author": "Anónimo"},
            {"quote": "Estudiar es aprender a ver con nuevos ojos.", "author": "Anónimo"},
            {"quote": "No dejes para mañana lo que puedas estudiar hoy.", "author": "Adaptación"},
            {"quote": "El conocimiento es el único tesoro que crece cuando se comparte.", "author": "Anónimo"},
            {"quote": "La disciplina es el puente entre metas y logros.", "author": "Jim Rohn"}
        ]
        
        # Lista de frases relacionadas con la motivación
        motivation_quotes = [
            {"quote": "El éxito no es la clave de la felicidad. La felicidad es la clave del éxito.", "author": "Albert Schweitzer"},
            {"quote": "El único modo de hacer un gran trabajo es amar lo que haces.", "author": "Steve Jobs"},
            {"quote": "No cuentes los días, haz que los días cuenten.", "author": "Muhammad Ali"},
            {"quote": "El mejor momento para plantar un árbol fue hace 20 años. El segundo mejor momento es ahora.", "author": "Proverbio chino"},
            {"quote": "El fracaso es la oportunidad de comenzar de nuevo, pero más inteligentemente.", "author": "Henry Ford"}
        ]
        
        # Seleccionar lista basada en el tema
        if topic.lower() in ["estudio", "estudiar", "study"]:
            quotes = study_quotes
        elif topic.lower() in ["motivación", "motivacion", "motivation"]:
            quotes = motivation_quotes
        else:
            # Si no hay coincidencia, devolver una mezcla
            quotes = study_quotes + motivation_quotes
            random.shuffle(quotes)
            quotes = quotes[:5]  # Limitar a 5 resultados
            
        return quotes