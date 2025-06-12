"""
Configuración de la base de datos SQLAlchemy para el sistema de inventario
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Query
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

class ActiveFilterMixin:
    """Mixin para agregar filtros de active_status automáticamente"""
    
    @classmethod
    def active_query(cls, session):
        """Query que solo devuelve registros activos (active_status = 1)"""
        return session.query(cls).filter(cls.active_status == 1)
    
    @classmethod
    def all_query(cls, session):
        """Query que devuelve todos los registros (incluyendo inactivos)"""
        return session.query(cls)
    
    @classmethod
    def get_active_by_id(cls, session, record_id):
        """Obtener registro activo por ID"""
        return session.query(cls).filter(
            cls.id == record_id,
            cls.active_status == 1
        ).first()

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
    
    @staticmethod
    def get_active_records(model_class, session=None):
        """Método genérico para obtener solo registros activos"""
        if session is None:
            session = DatabaseManager.get_session()
            close_session = True
        else:
            close_session = False
        
        try:
            # Verificar si el modelo tiene active_status
            if hasattr(model_class, 'active_status'):
                records = session.query(model_class).filter(model_class.active_status == 1).all()
            else:
                # Si no tiene active_status, devolver todos
                records = session.query(model_class).all()
            
            return records
        except Exception as e:
            logger.error(f"Error obteniendo registros activos de {model_class.__name__}: {e}")
            return []
        finally:
            if close_session:
                DatabaseManager.close_session(session)
    
    @staticmethod
    def soft_delete(model_class, record_id, session=None):
        """Eliminación lógica: cambiar active_status a 0"""
        if session is None:
            session = DatabaseManager.get_session()
            close_session = True
        else:
            close_session = False
        
        try:
            record = session.query(model_class).filter(model_class.id == record_id).first()
            if record and hasattr(record, 'active_status'):
                record.active_status = 0
                session.commit()
                logger.info(f"Registro {record_id} de {model_class.__name__} marcado como inactivo")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error en eliminación lógica de {model_class.__name__}: {e}")
            return False
        finally:
            if close_session:
                DatabaseManager.close_session(session)
    
    @staticmethod
    def restore_record(model_class, record_id, session=None):
        """Restaurar registro: cambiar active_status a 1"""
        if session is None:
            session = DatabaseManager.get_session()
            close_session = True
        else:
            close_session = False
        
        try:
            record = session.query(model_class).filter(model_class.id == record_id).first()
            if record and hasattr(record, 'active_status'):
                record.active_status = 1
                session.commit()
                logger.info(f"Registro {record_id} de {model_class.__name__} restaurado")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error restaurando registro de {model_class.__name__}: {e}")
            return False
        finally:
            if close_session:
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