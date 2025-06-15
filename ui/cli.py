import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Importaciones de nuestros módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.usuario import Usuario
from models.estudio import Estudio
from models.meta import Meta, PeriodoMeta
from database.mongo_client import MongoDBClient, MongoRepository
from api.quotes_api import QuotesAPI
from api.books_api import BooksAPI
from utils.stats import calcular_estadisticas

class CLI:
    """Interfaz de línea de comandos para la aplicación EduTracker."""
    
    def __init__(self, db_client: MongoDBClient):
        """
        Inicializa la interfaz CLI.
        
        Args:
            db_client: Cliente de MongoDB
        """
        self.db_client = db_client
        self.usuario_repo = MongoRepository(db_client, "usuarios", Usuario)
        self.estudio_repo = MongoRepository(db_client, "estudios", Estudio)
        self.meta_repo = MongoRepository(db_client, "metas", Meta)
        self.quotes_api = QuotesAPI()
        self.books_api = BooksAPI()
        self.usuario_actual = None
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal de la aplicación."""
        while True:
            self._limpiar_pantalla()
            
            if not self.usuario_actual:
                print("\n===== EduTracker - Monitor de Hábitos de Estudio =====")
                print("1. Iniciar sesión")
                print("2. Registrarse")
                print("0. Salir")
                
                opcion = input("\nSeleccione una opción: ")
                
                if opcion == "1":
                    self._iniciar_sesion()
                elif opcion == "2":
                    self._registrar_usuario()
                elif opcion == "0":
                    print("\n¡Gracias por usar EduTracker!")
                    sys.exit(0)
                else:
                    input("\nOpción inválida. Presione Enter para continuar...")
            else:
                self._mostrar_frase_motivacional()
                
                print(f"\n===== Bienvenido/a, {self.usuario_actual.nombre} =====")
                print("1. Registrar sesión de estudio")
                print("2. Ver mis sesiones de estudio")
                print("3. Establecer nueva meta")
                print("4. Ver mis metas")
                print("5. Ver estadísticas")
                print("6. Buscar recursos")
                print("7. Gestionar materias")
                print("8. Cerrar sesión")
                print("0. Salir")
                
                opcion = input("\nSeleccione una opción: ")
                
                if opcion == "1":
                    self._registrar_sesion_estudio()
                elif opcion == "2":
                    self._ver_sesiones_estudio()
                elif opcion == "3":
                    self._establecer_meta()
                elif opcion == "4":
                    self._ver_metas()
                elif opcion == "5":
                    self._ver_estadisticas()
                elif opcion == "6":
                    self._buscar_recursos()
                elif opcion == "7":
                    self._gestionar_materias()
                elif opcion == "8":
                    self.usuario_actual = None
                elif opcion == "0":
                    print("\n¡Gracias por usar EduTracker!")
                    sys.exit(0)
                else:
                    input("\nOpción inválida. Presione Enter para continuar...")
    
    def _limpiar_pantalla(self):
        """Limpia la pantalla de la consola."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _mostrar_frase_motivacional(self):
        """Muestra una frase motivacional aleatoria."""
        try:
            quote = self.quotes_api.get_random_quote()
            if quote:
                print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f'"{quote["quote"]}"')
                print(f'— {quote["author"]}')
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        except Exception:
            # Silenciosamente ignorar errores en la API de citas
            pass
    
    def _iniciar_sesion(self):
        """Permite al usuario iniciar sesión."""
        self._limpiar_pantalla()
        print("\n===== Iniciar Sesión =====")
        
        email = input("Email: ")
        password = input("Contraseña: ")
        
        # Buscar usuario por email
        usuarios = self.usuario_repo.find({"email": email})
        
        if not usuarios:
            input("\nUsuario no encontrado. Presione Enter para continuar...")
            return
        
        usuario = usuarios[0]
        
        # En una aplicación real, deberíamos verificar el hash de la contraseña
        # Aquí simplemente comparamos directamente (NO SEGURO)
        if password == usuario._Usuario__password:  # Accediendo al atributo privado
            self.usuario_actual = usuario
            input("\n¡Sesión iniciada correctamente! Presione Enter para continuar...")
        else:
            input("\nContraseña incorrecta. Presione Enter para continuar...")
    
    def _registrar_usuario(self):
        """Registra un nuevo usuario."""
        self._limpiar_pantalla()
        print("\n===== Registro de Usuario =====")
        
        nombre = input("Nombre completo: ")
        email = input("Email: ")
        password = input("Contraseña: ")
        
        # Verificar si el email ya está registrado
        usuarios_existentes = self.usuario_repo.find({"email": email})
        if usuarios_existentes:
            input("\nYa existe un usuario con ese email. Presione Enter para continuar...")
            return
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(nombre, email, password)
        self.usuario_repo.save(nuevo_usuario)
        
        input("\nUsuario registrado correctamente. Presione Enter para continuar...")
    
    def _registrar_sesion_estudio(self):
        """Registra una nueva sesión de estudio."""
        self._limpiar_pantalla()
        print("\n===== Registrar Sesión de Estudio =====")
        
        # Mostrar materias disponibles
        materias = self.usuario_actual.materias
        if not materias:
            input("\nNo tiene materias registradas. Añada materias primero. Presione Enter para continuar...")
            return
        
        print("\nMaterias disponibles:")
        for i, materia in enumerate(materias, 1):
            print(f"{i}. {materia}")
        
        # Seleccionar materia
        try:
            seleccion = int(input("\nSeleccione una materia (número): "))
            if seleccion < 1 or seleccion > len(materias):
                input("\nSelección inválida. Presione Enter para continuar...")
                return
            
            materia = materias[seleccion - 1]
        except ValueError:
            input("\nDebe ingresar un número. Presione Enter para continuar...")
            return
        
        # Ingresar duración
        try:
            duracion = int(input("\nDuración en minutos: "))
            if duracion <= 0:
                input("\nLa duración debe ser mayor a 0. Presione Enter para continuar...")
                return
        except ValueError:
            input("\nDebe ingresar un número. Presione Enter para continuar...")
            return
        
        # Ingresar notas (opcional)
        notas = input("\nNotas (opcional): ")
        
        # Crear y guardar la sesión de estudio
        sesion = Estudio(self.usuario_actual.id, materia, duracion, notas if notas else None)
        self.estudio_repo.save(sesion)
        
        # Verificar si se ha completado alguna meta
        self._verificar_metas_completadas(materia)
        
        input("\nSesión de estudio registrada correctamente. Presione Enter para continuar...")
    
    def _verificar_metas_completadas(self, materia: str):
        """
        Verifica si alguna meta se ha completado con la nueva sesión de estudio.
        
        Args:
            materia: Materia de la sesión de estudio
        """
        # Obtener metas activas para la materia
        metas_activas = self.meta_repo.find({
            "usuario_id": self.usuario_actual.id,
            "materia": materia,
            "completada": False
        })
        
        for meta in metas_activas:
            # Calcular fecha límite según el periodo
            if meta.periodo == PeriodoMeta.DIARIO:
                fecha_inicio = datetime.combine(meta.fecha_inicio.date(), datetime.min.time())
                fecha_fin = fecha_inicio + timedelta(days=1)
            elif meta.periodo == PeriodoMeta.SEMANAL:
                # Iniciar desde el lunes de la semana de inicio
                lunes = meta.fecha_inicio - timedelta(days=meta.fecha_inicio.weekday())
                fecha_inicio = datetime.combine(lunes.date(), datetime.min.time())
                fecha_fin = fecha_inicio + timedelta(days=7)
            elif meta.periodo == PeriodoMeta.MENSUAL:
                # Iniciar desde el primer día del mes
                primer_dia = meta.fecha_inicio.replace(day=1)
                fecha_inicio = datetime.combine(primer_dia.date(), datetime.min.time())
                # Calcular el primer día del siguiente mes
                if primer_dia.month == 12:
                    siguiente_mes = primer_dia.replace(year=primer_dia.year + 1, month=1)
                else:
                    siguiente_mes = primer_dia.replace(month=primer_dia.month + 1)
                fecha_fin = siguiente_mes
            
            # Obtener sesiones de estudio en el periodo
            sesiones = self.estudio_repo.find({
                "usuario_id": self.usuario_actual.id,
                "materia": materia,
                "fecha_hora": {"$gte": fecha_inicio, "$lt": fecha_fin}
            })
            
            # Sumar minutos estudiados
            minutos_totales = sum(sesion.duracion_minutos for sesion in sesiones)
            
            # Verificar si se ha alcanzado la meta
            if minutos_totales >= meta.minutos_objetivo:
                # Marcar meta como completada
                meta.completada = True
                self.meta_repo.update(meta)
                
                print(f"\n¡Felicidades! Has completado tu meta {meta.periodo.value} para {materia}.")
    
    def _ver_sesiones_estudio(self):
        """Muestra las sesiones de estudio del usuario."""
        self._limpiar_pantalla()
        print("\n===== Mis Sesiones de Estudio =====")
        
        # Obtener todas las sesiones del usuario
        sesiones = self.estudio_repo.find({"usuario_id": self.usuario_actual.id})
        
        if not sesiones:
            input("\nNo tienes sesiones de estudio registradas. Presione Enter para continuar...")
            return
        
        # Ordenar por fecha (de más reciente a más antigua)
        sesiones.sort(key=lambda s: s.fecha_hora, reverse=True)
        
        # Mostrar sesiones
        for i, sesion in enumerate(sesiones, 1):
            fecha_formateada = sesion.fecha_hora.strftime("%d/%m/%Y %H:%M")
            print(f"\n{i}. {sesion.materia} - {sesion.duracion_minutos} minutos - {fecha_formateada}")
            if sesion.notas:
                print(f"   Notas: {sesion.notas}")
        
        input("\nPresione Enter para continuar...")
    
    def _establecer_meta(self):
        """Establece una nueva meta de estudio."""
        self._limpiar_pantalla()
        print("\n===== Establecer Nueva Meta =====")
        
        # Mostrar materias disponibles
        materias = self.usuario_actual.materias
        if not materias:
            input("\nNo tiene materias registradas. Añada materias primero. Presione Enter para continuar...")
            return
        
        print("\nMaterias disponibles:")
        for i, materia in enumerate(materias, 1):
            print(f"{i}. {materia}")
        
        # Seleccionar materia
        try:
            seleccion = int(input("\nSeleccione una materia (número): "))
            if seleccion < 1 or seleccion > len(materias):
                input("\nSelección inválida. Presione Enter para continuar...")
                return
            
            materia = materias[seleccion - 1]
        except ValueError:
            input("\nDebe ingresar un número. Presione Enter para continuar...")
            return
        
        # Ingresar duración objetivo
        try:
            duracion = int(input("\nMinutos objetivo: "))
            if duracion <= 0:
                input("\nLos minutos objetivo deben ser mayor a 0. Presione Enter para continuar...")
                return
        except ValueError:
            input("\nDebe ingresar un número. Presione Enter para continuar...")
            return
        
        # Seleccionar periodo
        print("\nPeriodos disponibles:")
        print("1. Diario")
        print("2. Semanal")
        print("3. Mensual")
        
        try:
            periodo_seleccion = int(input("\nSeleccione un periodo (número): "))
            if periodo_seleccion < 1 or periodo_seleccion > 3:
                input("\nSelección inválida. Presione Enter para continuar...")
                return
            
            periodos = [PeriodoMeta.DIARIO, PeriodoMeta.SEMANAL, PeriodoMeta.MENSUAL]
            periodo = periodos[periodo_seleccion - 1]
        except ValueError:
            input("\nDebe ingresar un número. Presione Enter para continuar...")
            return
        
        # Crear y guardar la meta
        meta = Meta(self.usuario_actual.id, materia, duracion, periodo)
        self.meta_repo.save(meta)
        
        input("\nMeta establecida correctamente. Presione Enter para continuar...")
    
    def _ver_metas(self):
        """Muestra las metas del usuario."""
        self._limpiar_pantalla()
        print("\n===== Mis Metas =====")
        
        # Obtener todas las metas del usuario
        metas = self.meta_repo.find({"usuario_id": self.usuario_actual.id})
        
        if not metas:
            input("\nNo tienes metas establecidas. Presione Enter para continuar...")
            return
        
        # Ordenar por fecha (de más reciente a más antigua)
        metas.sort(key=lambda m: m.fecha_inicio, reverse=True)
        
        # Mostrar metas
        for i, meta in enumerate(metas, 1):
            fecha_formateada = meta.fecha_inicio.strftime("%d/%m/%Y")
            estado = "✓ Completada" if meta.completada else "⬚ Pendiente"
            
            print(f"\n{i}. {meta.materia} - {meta.minutos_objetivo} minutos ({meta.periodo.value})")
            print(f"   Inicio: {fecha_formateada} - Estado: {estado}")
        
        input("\nPresione Enter para continuar...")
    
    def _ver_estadisticas(self):
        """Muestra estadísticas de estudio del usuario."""
        self._limpiar_pantalla()
        print("\n===== Mis Estadísticas =====")
        
        # Obtener todas las sesiones del usuario
        sesiones = self.estudio_repo.find({"usuario_id": self.usuario_actual.id})
        
        if not sesiones:
            input("\nNo tienes sesiones de estudio registradas. Presione Enter para continuar...")
            return
        
        # Calcular estadísticas usando la función del módulo stats
        estadisticas = calcular_estadisticas(sesiones)
        
        # Mostrar estadísticas generales
        print(f"\nTotal de sesiones: {estadisticas['total_sesiones']}")
        print(f"Total de minutos estudiados: {estadisticas['total_minutos']}")
        
        # Mostrar minutos por materia
        print("\nMinutos por materia:")
        for materia, minutos in estadisticas['minutos_por_materia'].items():
            print(f"- {materia}: {minutos} minutos")
        
        # Mostrar distribución por día de la semana
        print("\nDistribución por día de la semana:")
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        for i, minutos in enumerate(estadisticas['minutos_por_dia_semana']):
            print(f"- {dias[i]}: {minutos} minutos")
        
        # Mostrar promedio diario en la última semana
        print(f"\nPromedio diario (última semana): {estadisticas['promedio_diario_ultima_semana']} minutos")
        
        input("\nPresione Enter para continuar...")
    
    def _buscar_recursos(self):
        """Busca recursos relacionados con las materias."""
        self._limpiar_pantalla()
        print("\n===== Buscar Recursos =====")
        
        # Mostrar materias disponibles
        materias = self.usuario_actual.materias
        if not materias:
            input("\nNo tiene materias registradas. Añada materias primero. Presione Enter para continuar...")
            return
        
        print("\nMaterias disponibles:")
        for i, materia in enumerate(materias, 1):
            print(f"{i}. {materia}")
        
        # Seleccionar materia
        try:
            seleccion = int(input("\nSeleccione una materia (número): "))
            if seleccion < 1 or seleccion > len(materias):
                input("\nSelección inválida. Presione Enter para continuar...")
                return
            
            materia = materias[seleccion - 1]
        except ValueError:
            input("\nDebe ingresar un número. Presione Enter para continuar...")
            return
        
        # Buscar libros relacionados
        print(f"\nBuscando libros relacionados con '{materia}'...")
        libros = self.books_api.get_book_by_subject(materia)
        
        if not libros:
            print("\nNo se encontraron libros relacionados.")
        else:
            print("\nLibros recomendados:")
            for i, libro in enumerate(libros, 1):
                autores = ", ".join(libro["authors"])
                print(f"\n{i}. {libro['title']} ({libro['year']})")
                print(f"   Autor(es): {autores}")
                if "subjects" in libro and libro["subjects"]:
                    temas = ", ".join(libro["subjects"][:3])  # Mostrar solo los primeros 3 temas
                    print(f"   Temas: {temas}")
        
        input("\nPresione Enter para continuar...")
    
    def _gestionar_materias(self):
        """Gestiona las materias del usuario."""
        while True:
            self._limpiar_pantalla()
            print("\n===== Gestionar Materias =====")
            
            # Mostrar materias actuales
            materias = self.usuario_actual.materias
            if materias:
                print("\nMaterias actuales:")
                for i, materia in enumerate(materias, 1):
                    print(f"{i}. {materia}")
            else:
                print("\nNo tienes materias registradas.")
            
            print("\n1. Agregar materia")
            print("2. Eliminar materia")
            print("0. Volver al menú principal")
            
            opcion = input("\nSeleccione una opción: ")
            
            if opcion == "1":
                self._agregar_materia()
            elif opcion == "2":
                self._eliminar_materia()
            elif opcion == "0":
                break
            else:
                input("\nOpción inválida. Presione Enter para continuar...")
    
    def _agregar_materia(self):
        """Agrega una nueva materia."""
        nueva_materia = input("\nNombre de la nueva materia: ")
        
        if not nueva_materia:
            input("\nEl nombre de la materia no puede estar vacío. Presione Enter para continuar...")
            return
        
        # Verificar si la materia ya existe
        if nueva_materia in self.usuario_actual.materias:
            input("\nEsa materia ya está registrada. Presione Enter para continuar...")
            return
        
        # Agregar materia
        self.usuario_actual.agregar_materia(nueva_materia)
        
        # Actualizar en la base de datos
        self.usuario_repo.update(self.usuario_actual)
        
        input("\nMateria agregada correctamente. Presione Enter para continuar...")
    
    def _eliminar_materia(self):
        """Elimina una materia existente."""
        # Verificar si hay materias
        materias = self.usuario_actual.materias
        if not materias:
            input("\nNo tienes materias para eliminar. Presione Enter para continuar...")
            return
        
        try:
            seleccion = int(input("\nNúmero de la materia a eliminar: "))
            if seleccion < 1 or seleccion > len(materias):
                input("\nSelección inválida. Presione Enter para continuar...")
                return
            
            materia = materias[seleccion - 1]
        except ValueError:
            input("\nDebe ingresar un número. Presione Enter para continuar...")
            return
        
        # Confirmar eliminación
        confirmacion = input(f"\n¿Está seguro de eliminar la materia '{materia}'? (s/n): ")
        if confirmacion.lower() != "s":
            input("\nOperación cancelada. Presione Enter para continuar...")
            return
        
        # Eliminar materia
        self.usuario_actual.eliminar_materia(materia)
        
        # Actualizar en la base de datos
        self.usuario_repo.update(self.usuario_actual)
        
        input("\nMateria eliminada correctamente. Presione Enter para continuar...")