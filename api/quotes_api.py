import requests
import random
from datetime import datetime

class QuotesAPI:
    """Clase para interactuar con la API de ZenQuotes."""
    
    def __init__(self):
        # Algunas citas predeterminadas por si la API falla
        self.default_quotes = [
            {"quote": "La educación es el arma más poderosa que puedes usar para cambiar el mundo.", "author": "Nelson Mandela"},
            {"quote": "La educación es el pasaporte hacia el futuro, el mañana pertenece a aquellos que se preparan para él en el día de hoy.", "author": "Malcolm X"},
            {"quote": "El aprendizaje es como remar contra corriente: en cuanto se deja, se retrocede.", "author": "Edward Benjamin Britten"},
        ]
        
    def get_random_quote(self):
        """
        Obtiene una frase motivacional aleatoria.
        
        Returns:
            Diccionario con la frase y el autor, o None si hay un error
        """
        try:
            response = requests.get("https://api.quotable.io/random?tags=education,learning")
            response.raise_for_status()
            data = response.json()
            return {
                "quote": data.get("content"),
                "author": data.get("author")
            }
        except Exception:
            # Fallback a citas predeterminadas
            return random.choice(self.default_quotes)
    
    def get_daily_quote(self):
        """
        Obtiene la frase motivacional del día.
        
        Returns:
            Diccionario con la frase y el autor, o None si hay un error
        """
        # Usar la fecha actual como semilla para tener la misma cita durante todo el día
        day_of_year = datetime.now().timetuple().tm_yday
        random.seed(day_of_year)
        try:
            response = requests.get("https://api.quotable.io/quotes?tags=education,learning&limit=20")
            response.raise_for_status()
            data = response.json()
            quotes = data.get("results", [])
            if quotes:
                quote_index = day_of_year % len(quotes)
                quote = quotes[quote_index]
                random.seed()  # Restablecer la semilla
                return {
                    "quote": quote.get("content"),
                    "author": quote.get("author")
                }
        except Exception:
            pass
            
        # Fallback a citas predeterminadas
        quote = self.default_quotes[day_of_year % len(self.default_quotes)]
        random.seed()  # Restablecer la semilla
        return quote
    
    def get_quotes_by_topic(self, topic: str):
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