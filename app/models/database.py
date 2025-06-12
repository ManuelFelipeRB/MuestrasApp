"""
Configuración de la base de datos SQLAlchemy para el sistema de inventario
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging
from config import DATABASE_CONFIG
from app.utils.constants import FIXED_WAREHOUSES

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base para los modelos
Base = declarative_base()

# Crear engine de SQLAlchemy
engine = create_engine(
    DATABASE_CONFIG["url"],
    echo=DATABASE_CONFIG["echo"],
    future=DATABASE_CONFIG["future"],
    pool_pre_ping=DATABASE_CONFIG["pool_pre_ping"],
    # Configuración específica para SQLite
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    }
)

# Crear sessionmaker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class DatabaseManager:
    """Gestor de la base de datos"""
    
    @staticmethod
    def create_tables():
        """Crear todas las tablas en la base de datos"""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Tablas creadas exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error al crear tablas: {e}")
            return False
    
    @staticmethod
    def get_session():
        """Obtener una sesión de base de datos"""
        session = SessionLocal()
        try:
            return session
        except Exception as e:
            session.close()
            logger.error(f"Error al crear sesión: {e}")
            raise
    
    @staticmethod
    def close_session(session):
        """Cerrar una sesión de base de datos"""
        try:
            session.close()
        except Exception as e:
            logger.error(f"Error al cerrar sesión: {e}")
    
    @staticmethod
    def init_fixed_data():
        """Inicializar datos fijos (bodegas)"""
        from app.models.warehouse import Warehouse
        
        session = DatabaseManager.get_session()
        try:
            # Verificar si ya existen las bodegas
            existing_warehouses = session.query(Warehouse).count()
            
            if existing_warehouses == 0:
                logger.info("Inicializando bodegas fijas...")
                
                for warehouse_data in FIXED_WAREHOUSES:
                    warehouse = Warehouse(
                        code=warehouse_data["code"],
                        name=warehouse_data["name"], 
                        description=warehouse_data["description"],
                        capacity=warehouse_data["capacity"],
                        active_status=True
                    )
                    session.add(warehouse)
                
                session.commit()
                logger.info(f"Se crearon {len(FIXED_WAREHOUSES)} bodegas fijas")
            else:
                logger.info("Las bodegas ya están inicializadas")
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error al inicializar datos fijos: {e}")
            raise
        finally:
            DatabaseManager.close_session(session)

# Función para obtener sesión de DB (dependency injection para FastAPI)
def get_db():
    """Dependency para obtener sesión de base de datos en FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Event listeners para SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configurar pragmas de SQLite para mejor rendimiento"""
    cursor = dbapi_connection.cursor()
    # Habilitar foreign keys
    cursor.execute("PRAGMA foreign_keys=ON")
    # Configurar journal mode para mejor concurrencia
    cursor.execute("PRAGMA journal_mode=WAL") 
    # Configurar sincronización para mejor rendimiento
    cursor.execute("PRAGMA synchronous=NORMAL")
    # Configurar timeout para transacciones
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.close()

# Función de inicialización completa
def initialize_database():
    """Inicializar completamente la base de datos"""
    try:
        logger.info("Inicializando base de datos...")
        
        # Crear tablas
        if DatabaseManager.create_tables():
            logger.info("Base de datos inicializada correctamente")
            
            # Inicializar datos fijos
            DatabaseManager.init_fixed_data()
            
            return True
        else:
            logger.error("Error en la inicialización de la base de datos")
            return False
            
    except Exception as e:
        logger.error(f"Error crítico en inicialización: {e}")
        return False