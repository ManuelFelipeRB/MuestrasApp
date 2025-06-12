"""
Inicialización del módulo de modelos
Importando modelos gradualmente para evitar errores de dependencias
"""

# Importar la base de datos primero
from .database import Base, engine, SessionLocal, DatabaseManager, get_db, initialize_database

# Importar modelos en orden de dependencias
from .warehouse import Warehouse
from .client import Client
from .mine import Mine
from .batch import Batch
from .batch_warehouse import BatchWarehouse

# Exportar todos los modelos disponibles
__all__ = [
    'Base',
    'engine', 
    'SessionLocal',
    'DatabaseManager',
    'get_db',
    'initialize_database',
    'Warehouse',
    'Client',
    'Mine',
    'Batch',
    'BatchWarehouse'
]