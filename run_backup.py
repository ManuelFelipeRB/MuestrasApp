
"""
Sistema de Control de Inventario de Laboratorio
Aplicación desktop para gestión de muestras de laboratorio con Flet
"""

import os
import sys
import logging
import flet as ft

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_project_structure():
    """Crear estructura de carpetas del proyecto"""
    logger.info("Estructura del proyecto creada")
    
    # Carpetas principales
    directories = [
        "app",
        "app/models", 
        "app/services",
        "app/ui",
        "data",
        "assets"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Crear __init__.py files
    init_files = [
        "app/__init__.py",
        "app/models/__init__.py", 
        "app/services/__init__.py",
        "app/ui/__init__.py"
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8") as f:
                module_name = init_file.split("/")[1] if "/" in init_file else "app"
                f.write(f'"""{module_name.title()} module"""\n')

def initialize_database():
    """Inicializar base de datos y datos de prueba"""
    try:
        logger.info("Inicializando base de datos...")
        
        # IMPORTANTE: Eliminar base de datos existente para recrear con estructura correcta
        import os
        db_path = "data/inventory.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info("Base de datos existente eliminada para recrear")
        
        # También eliminar cualquier archivo de base de datos en el directorio raíz
        root_db_path = "inventory.db"
        if os.path.exists(root_db_path):
            os.remove(root_db_path)
            logger.info("Base de datos en directorio raíz eliminada")
        
        # Limpiar cualquier archivo .db que pueda existir
        for file in os.listdir("."):
            if file.endswith(".db"):
                os.remove(file)
                logger.info(f"Archivo de BD {file} eliminado")
        
        from app.models.database import initialize_database
        initialize_database()
        logger.info("Base de datos inicializada correctamente")
        
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        raise

def verify_database():
    """Verificar que la base de datos funciona correctamente"""
    try:
        logger.info("Verificando base de datos...")
        from app.models.database import DatabaseManager
        from app.models.warehouse import Warehouse
        
        session = DatabaseManager.get_session()
        try:
            warehouse_count = session.query(Warehouse).count()
            logger.info(f"Bodegas configuradas: {warehouse_count}")
            
            if warehouse_count == 0:
                logger.warning("No hay bodegas configuradas")
            else:
                logger.info("Base de datos verificada correctamente")
                
        finally:
            DatabaseManager.close_session(session)
            
    except Exception as e:
        logger.error(f"Error verificando base de datos: {e}")
        raise

def main_app(page: ft.Page):
    """Aplicación principal con interfaz de muestras"""
    page.title = "Sistema de Control de Inventario - Muestras"
    page.window_width = 1200
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    try:
        # Verificar si existe la vista de muestras
        if os.path.exists("app/ui/samples_view.py"):
            # Importar la vista de muestras
            from app.ui.samples_view import SamplesView
            
            # Crear vista de muestras
            samples_view = SamplesView(page)
            
            # Agregar a la página
            page.add(samples_view.get_view())
            page.update()
        else:
            # Interfaz de fallback simple
            page.add(
                ft.Container(
                    content=ft.Column([
                        ft.Text("🧪 Sistema de Control de Inventario", 
                               size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Laboratorio de Análisis de Muestras", 
                               size=16, color=ft.Colors.GREY_700),
                        ft.Divider(),
                        ft.Text("⚠️ Interfaz de muestras no encontrada", 
                               size=18, color=ft.Colors.ORANGE_600),
                        ft.Text("Cree el archivo: app/ui/samples_view.py", 
                               size=14, color=ft.Colors.GREY_600),
                        ft.ElevatedButton(
                            "🔄 Reiniciar",
                            on_click=lambda _: page.window.close()
                        )
                    ], 
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15),
                    padding=40,
                    alignment=ft.alignment.center,
                    expand=True
                )
            )
            page.update()
        
    except ImportError as e:
        # Error de importación - mostrar mensaje específico
        error_container = ft.Container(
            content=ft.Column([
                ft.Text("❌ Error de Importación", size=20, color=ft.Colors.RED_600),
                ft.Text("Archivos faltantes:", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("• app/ui/samples_view.py", size=14, color=ft.Colors.GREY_700),
                ft.Text("• app/services/sample_service.py", size=14, color=ft.Colors.GREY_700),
                ft.Divider(),
                ft.Text(f"Error específico: {str(e)}", size=12, color=ft.Colors.RED_400),
                ft.ElevatedButton(
                    "🔄 Reintentar",
                    on_click=lambda _: page.window.close()
                )
            ], alignment=ft.MainAxisAlignment.CENTER,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               spacing=10),
            alignment=ft.alignment.center,
            expand=True,
            padding=40
        )
        page.add(error_container)
        page.update()
        
    except Exception as e:
        # Error general
        error_container = ft.Container(
            content=ft.Column([
                ft.Text("❌ Error cargando la aplicación", size=20, color=ft.Colors.RED_600),
                ft.Text(str(e), size=14, color=ft.Colors.GREY_700),
                ft.ElevatedButton(
                    "🔄 Reintentar",
                    on_click=lambda _: page.window.close()
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
        page.add(error_container)
        page.update()

def start_flet_app():
    """Iniciar aplicación Flet con interfaz de muestras"""
    logger.info("Iniciando aplicación Flet...")
    ft.app(target=main_app, assets_dir="assets")

def main():
    """Función principal"""
    try:
        logger.info("=== Sistema de Control de Inventario de Laboratorio ===")
        logger.info("Iniciando aplicación...")
        
        # 1. Crear estructura de proyecto
        create_project_structure()
        
        # 2. Inicializar base de datos
        initialize_database()
        
        # 3. Verificar base de datos
        verify_database()
        
        # 4. Iniciar interfaz
        logger.info("Sistema listo. Iniciando interfaz...")
        start_flet_app()
        
    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por usuario")
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        sys.exit(1)
    finally:
        logger.info("Aplicación finalizada")

if __name__ == "__main__":
    main()