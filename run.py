"""
Script principal para ejecutar el Sistema de Inventario de Laboratorio
Versión simplificada sin conflictos de asyncio
"""
import sys
import logging
from pathlib import Path

# Agregar el directorio raíz al path de Python
sys.path.append(str(Path(__file__).parent))

from app.models.database import initialize_database
from config import FLET_CONFIG

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
        "app/views/components/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch(exist_ok=True)
    
    logger.info("Estructura del proyecto creada")

def start_flet_app():
    """Iniciar la aplicación Flet"""
    import flet as ft
    
    try:
        logger.info("Iniciando aplicación Flet...")
        
        # Importar la aplicación principal
        from app.main import main
        
        # Ejecutar la aplicación Flet (versión simplificada)
        ft.app(
            target=main,
            name=FLET_CONFIG["page_title"],
            port=8080
        )
        
    except Exception as e:
        logger.error(f"Error al iniciar aplicación Flet: {e}")

def run_application():
    """Ejecutar la aplicación completa (sin asyncio)"""
    try:
        # 1. Configurar estructura del proyecto
        setup_project_structure()
        
        # 2. Inicializar base de datos
        logger.info("Inicializando base de datos...")
        if not initialize_database():
            logger.error("Error en inicialización de base de datos")
            return False
        
        # 3. Verificar que la base esté funcionando
        logger.info("Verificando base de datos...")
        try:
            from app.models.database import DatabaseManager
            session = DatabaseManager.get_session()
            
            # Verificar que las bodegas estén creadas
            from app.utils.constants import FIXED_WAREHOUSES
            logger.info(f"Bodegas configuradas: {len(FIXED_WAREHOUSES)}")
            
            DatabaseManager.close_session(session)
            logger.info("Base de datos verificada correctamente")
            
        except Exception as e:
            logger.warning(f"Verificación de base de datos falló: {e}")
        
        # 4. Iniciar aplicación Flet
        logger.info("Sistema listo. Iniciando interfaz...")
        start_flet_app()
        
        return True
        
    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {e}")
        return False

def main():
    """Función principal"""
    logger.info("=== Sistema de Control de Inventario de Laboratorio ===")
    logger.info("Iniciando aplicación...")
    
    try:
        # Ejecutar la aplicación (sin asyncio)
        run_application()
        
    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por el usuario")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
    finally:
        logger.info("Aplicación finalizada")

if __name__ == "__main__":
    main()