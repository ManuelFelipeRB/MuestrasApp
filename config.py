"""
Configuración global del Sistema de Inventario de Laboratorio
"""
import os
from pathlib import Path

# Rutas del proyecto
BASE_DIR = Path(__file__).parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/inventory.db"

# Configuración de la base de datos
DATABASE_CONFIG = {
    "url": DATABASE_URL,
    "echo": False,  # Set to True for SQL debugging
    "future": True,
    "pool_pre_ping": True,
}

# Configuración de Flet
FLET_CONFIG = {
    "page_title": "Control de Inventario - Laboratorio",
    "window_width": 1200,
    "window_height": 800,
    "window_min_width": 800,
    "window_min_height": 600,
    "theme_mode": "light",  # light, dark, system
}

# Configuración de auditoría
AUDIT_CONFIG = {
    "enabled": True,
    "max_old_value_length": 1000,  # Máximo caracteres para valores antiguos en JSON
    "default_user": "system",  # Usuario por defecto cuando no se especifica
}

# Configuración de paginación
PAGINATION_CONFIG = {
    "default_page_size": 50,
    "max_page_size": 200,
}

# Crear directorio de base de datos si no existe
DATABASE_DIR.mkdir(exist_ok=True)