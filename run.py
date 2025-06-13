"""
Script principal para ejecutar el Sistema de Inventario de Laboratorio
Versión simplificada sin conflictos de threading
"""
import sys
import flet as ft
import logging
from pathlib import Path

# Agregar el directorio raíz al path de Python
sys.path.append(str(Path(__file__).parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_project_structure():
    """Crear la estructura de directorios del proyecto"""
    directories = [
        "app",
        "app/api",
        "app/api/routes", 
        "app/controllers",
        "app/models",
        "app/services", 
        "app/utils",
        "app/views",
        "app/views/components",
        "app/ui",  # ← DIRECTORIO PARA UI
        "database"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Crear archivos __init__.py
    init_files = [
        "app/__init__.py",
        "app/api/__init__.py", 
        "app/api/routes/__init__.py",
        "app/controllers/__init__.py",
        "app/services/__init__.py",
        "app/utils/__init__.py",
        "app/views/__init__.py",
        "app/views/components/__init__.py",
        "app/ui/__init__.py"  # ← INIT PARA UI
    ]
    
    for init_file in init_files:
        Path(init_file).touch(exist_ok=True)
    
    logger.info("Estructura del proyecto creada")

def initialize_app():
    """Inicializar la aplicación (base de datos, etc.)"""
    try:
        # 1. Configurar estructura del proyecto
        setup_project_structure()
        
        # 2. Inicializar base de datos
        logger.info("Inicializando base de datos...")
        from app.models.database import initialize_database
        
        if not initialize_database():
            logger.error("Error en inicialización de base de datos")
            return False
        
        # 3. Verificar que la base esté funcionando
        logger.info("Verificando base de datos...")
        from app.models.database import DatabaseManager
        from app.utils.constants import FIXED_WAREHOUSES
        
        session = DatabaseManager.get_session()
        logger.info(f"Bodegas configuradas: {len(FIXED_WAREHOUSES)}")
        DatabaseManager.close_session(session)
        logger.info("Base de datos verificada correctamente")
        
        return True
        
    except Exception as e:
        logger.error(f"Error en inicialización: {e}")
        return False

def main(page: ft.Page):
    """Función principal de Flet"""
    logger.info("=== Sistema de Control de Inventario de Laboratorio ===")
    logger.info("Iniciando aplicación...")
    
    try:
        # Inicializar la aplicación
        if not initialize_app():
            page.add(ft.Text("❌ Error en inicialización", color=ft.Colors.RED))
            page.update()
            return
        
        logger.info("Sistema listo. Iniciando interfaz...")
        
        # Importar y ejecutar la aplicación principal
        from app.main import main as app_main
        app_main(page)
        
    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {e}")
        page.add(ft.Container(
            content=ft.Column([
                ft.Text(f"❌ Error: {str(e)}", size=16, color=ft.Colors.RED),
                ft.Text("Verificar estructura del proyecto", size=14),
            ]),
            padding=20
        ))
        page.update()

if __name__ == "__main__":
    
    ft.app(target=main, view=ft.WEB_BROWSER, port=8080)