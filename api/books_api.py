import requests
from typing import Dict, List, Optional, Any

class BooksAPI:
    """Clase para interactuar con la API de OpenLibrary."""
    
    def __init__(self):
        self.base_url = "https://openlibrary.org/api"
        
    def search_books(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Busca libros por título, autor o tema.
        
        Args:
            query: Término de búsqueda
            limit: Número máximo de resultados
            
        Returns:
            Lista de libros encontrados
        """
        try:
            url = f"https://openlibrary.org/search.json"
            params = {
                "q": query,
                "limit": limit
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for doc in data.get("docs", [])[:limit]:
                    book = {
                        "title": doc.get("title", "Sin título"),
                        "authors": [author for author in doc.get("author_name", ["Autor desconocido"])],
                        "year": doc.get("first_publish_year", "Año desconocido"),
                        "subjects": doc.get("subject", [])[:5] if doc.get("subject") else [],
                    }
                    
                    # Agregar URL de la portada si está disponible
                    if doc.get("cover_i"):
                        book["cover_url"] = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
                    
                    results.append(book)
                
                return results
            
            return []
        except Exception as e:
            print(f"Error al buscar libros: {str(e)}")
            return []
    
    def get_book_by_subject(self, subject: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Obtiene libros por tema/materia.
        
        Args:
            subject: Tema o materia
            limit: Número máximo de resultados
            
        Returns:
            Lista de libros encontrados
        """
        # Usamos el endpoint de búsqueda con el tema como consulta
        return self.search_books(f"subject:{subject}", limit)
    
    def get_book_details(self, olid: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un libro por su ID de OpenLibrary.
        
        Args:
            olid: OpenLibrary ID
            
        Returns:
            Detalles del libro o None si hay un error
        """
        try:
            url = f"https://openlibrary.org/works/{olid}.json"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extraer información relevante
                book_details = {
                    "title": data.get("title", "Sin título"),
                    "description": data.get("description", "Sin descripción"),
                    "subjects": data.get("subjects", [])[:10] if data.get("subjects") else [],
                }
                
                # Intentar obtener la portada
                if data.get("covers") and len(data["covers"]) > 0:
                    book_details["cover_url"] = f"https://covers.openlibrary.org/b/id/{data['covers'][0]}-L.jpg"
                
                return book_details
            
            return None
        except Exception as e:
            print(f"Error al obtener detalles del libro: {str(e)}")
            return None