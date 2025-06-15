from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

def calcular_estadisticas(sesiones: List[Any]) -> Dict[str, Any]:
    """
    Calcula estadísticas basadas en las sesiones de estudio.
    
    Args:
        sesiones: Lista de objetos Estudio
        
    Returns:
        Diccionario con estadísticas calculadas
    """
    if not sesiones:
        return {
            "total_sesiones": 0,
            "total_minutos": 0,
            "minutos_por_materia": {},
            "minutos_por_dia_semana": [0] * 7,
            "promedio_diario_ultima_semana": 0
        }
    
    # Inicializar estadísticas
    total_sesiones = len(sesiones)
    total_minutos = 0
    minutos_por_materia = defaultdict(int)
    minutos_por_dia_semana = [0] * 7  # Lunes a Domingo
    
    # Calcular minutos por materia y por día de la semana
    for sesion in sesiones:
        total_minutos += sesion.duracion_minutos
        minutos_por_materia[sesion.materia] += sesion.duracion_minutos
        
        # Día de la semana (0 = Lunes, 6 = Domingo)
        dia_semana = sesion.fecha_hora.weekday()
        minutos_por_dia_semana[dia_semana] += sesion.duracion_minutos
    
    # Calcular promedio diario en la última semana
    fecha_actual = datetime.now()
    una_semana_atras = fecha_actual - timedelta(days=7)
    
    sesiones_ultima_semana = [s for s in sesiones if s.fecha_hora >= una_semana_atras]
    minutos_ultima_semana = sum(s.duracion_minutos for s in sesiones_ultima_semana)
    
    # Evitar división por cero
    promedio_diario_ultima_semana = round(minutos_ultima_semana / 7, 1)
    
    return {
        "total_sesiones": total_sesiones,
        "total_minutos": total_minutos,
        "minutos_por_materia": dict(minutos_por_materia),
        "minutos_por_dia_semana": minutos_por_dia_semana,
        "promedio_diario_ultima_semana": promedio_diario_ultima_semana
    }