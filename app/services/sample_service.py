"""
Servicio para gestión de muestras de laboratorio
Maneja todas las operaciones CRUD y lógica de negocio
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.database import DatabaseManager
from app.models.sample import Sample
from app.models.batch import Batch
from app.models.warehouse import Warehouse
from app.models.client import Client

logger = logging.getLogger(__name__)

class SampleService:
    """Servicio para gestión de muestras"""
    
    # En app/services/sample_service.py
    @staticmethod
    def get_all_samples(active_only: bool = True) -> List[Sample]:  # ← Cambiar tipo de retorno
        """Obtener todas las muestras"""
        session = DatabaseManager.get_session()
        try:
            query = session.query(Sample)
            if active_only:
                query = query.filter(Sample.active_status == True)
            
            samples = query.order_by(Sample.created_at.desc()).all()
            return samples  # ❌ CAMBIAR: No usar to_dict()
            
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_sample_by_id(sample_id: int) -> Optional[Sample]:
        """Obtener muestra por ID"""
        session = DatabaseManager.get_session()
        try:
            sample = session.query(Sample).filter(Sample.id == sample_id).first()
            return sample
        except Exception as e:
            logger.error(f"Error obteniendo muestra {sample_id}: {e}")
            raise
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_sample_by_code(sample_code: str) -> Optional[Sample]:
        """Obtener muestra por código"""
        session = DatabaseManager.get_session()
        try:
            sample = session.query(Sample).filter(Sample.sample_code == sample_code).first()
            return sample
        except Exception as e:
            logger.error(f"Error obteniendo muestra {sample_code}: {e}")
            raise
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def create_sample(sample_data: Dict[str, Any]) -> Sample:
        """Crear nueva muestra"""
        session = DatabaseManager.get_session()
        try:
            # Validar que el código no exista
            existing = session.query(Sample).filter(Sample.sample_code == sample_data.get('sample_code')).first()
            if existing:
                raise ValueError(f"Ya existe una muestra con código {sample_data.get('sample_code')}")
            
            # Crear nueva muestra
            sample = Sample(
                batch_id=sample_data.get('batch_id'),
                sample_code=sample_data.get('sample_code'),
                description=sample_data.get('description', ''),
                extraction_date=sample_data.get('extraction_date', datetime.now()),
                quantity=sample_data.get('quantity', 0.0),
                unit=sample_data.get('unit', 'g'),
                client_id=sample_data.get('client_id'),
                warehouse_id=sample_data.get('warehouse_id'),
                seal_code=sample_data.get('seal_code', ''),
                storage_location=sample_data.get('storage_location', ''),
                observations=sample_data.get('observations', ''),
                status=sample_data.get('status', 'EXTRACTED'),
                lab_notes=sample_data.get('lab_notes', ''),
                test_results=sample_data.get('test_results', ''),
                tested_date=sample_data.get('tested_date'),
                active_status=sample_data.get('active_status', True),
                user= sample_data.get('user', 'system'),
            )
            
            session.add(sample)
            session.commit()
            session.refresh(sample)
            
            logger.info(f"Muestra creada: {sample.sample_code} (ID: {sample.id})")
            return sample
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error creando muestra: {e}")
            raise
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def update_sample(sample_id: int, sample_data: Dict[str, Any]) -> Sample:
        """Actualizar muestra existente"""
        session = DatabaseManager.get_session()
        try:
            sample = session.query(Sample).filter(Sample.id == sample_id).first()
            if not sample:
                raise ValueError(f"Muestra con ID {sample_id} no encontrada")
            
            # Actualizar campos
            for field, value in sample_data.items():
                if hasattr(sample, field) and value is not None:
                    setattr(sample, field, value)
            
            sample.updated_at = datetime.now()
            session.commit()
            session.refresh(sample)
            
            logger.info(f"Muestra actualizada: {sample.sample_code} (ID: {sample.id})")
            return sample
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error actualizando muestra {sample_id}: {e}")
            raise
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def delete_sample(sample_id: int) -> bool:
        """Eliminar muestra (soft delete)"""
        session = DatabaseManager.get_session()
        try:
            sample = session.query(Sample).filter(Sample.id == sample_id).first()
            if not sample:
                raise ValueError(f"Muestra con ID {sample_id} no encontrada")
            
            sample.active_status = False
            sample.updated_at = datetime.now()
            session.commit()
            
            logger.info(f"Muestra eliminada: {sample.sample_code} (ID: {sample.id})")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error eliminando muestra {sample_id}: {e}")
            raise
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def search_samples(search_term: str = "", status_filter: str = "ALL", limit: int = 100) -> List[Sample]:
        """Buscar muestras con filtros"""
        session = DatabaseManager.get_session()
        try:
            query = session.query(Sample)
            
            # Filtro por término de búsqueda
            if search_term:
                query = query.filter(
                    or_(
                        Sample.sample_code.ilike(f"%{search_term}%"),
                        Sample.description.ilike(f"%{search_term}%"),
                        Sample.observations.ilike(f"%{search_term}%")
                    )
                )
            
            # Filtro por estado
            if status_filter != "ALL":
                if status_filter == "ACTIVE":
                    query = query.filter(Sample.active_status == True)
                elif status_filter == "INACTIVE":
                    query = query.filter(Sample.active_status == False)
                else:
                    query = query.filter(Sample.status == status_filter)
            
            samples = query.order_by(desc(Sample.created_at)).limit(limit).all()
            return samples
            
        except Exception as e:
            logger.error(f"Error buscando muestras: {e}")
            raise
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_batches() -> List[Batch]:
        """Obtener todos los lotes disponibles"""
        session = DatabaseManager.get_session()
        try:
            batches = session.query(Batch).filter(Batch.active_status == True).all()
            return batches
        except Exception as e:
            logger.error(f"Error obteniendo lotes: {e}")
            raise
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_warehouses() -> List[Warehouse]:
        """Obtener todas las bodegas disponibles"""
        session = DatabaseManager.get_session()
        try:
            warehouses = session.query(Warehouse).all()
            return warehouses
        except Exception as e:
            logger.error(f"Error obteniendo bodegas: {e}")
            raise
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_clients() -> List[Client]:
        """Obtener todos los clientes disponibles"""
        session = DatabaseManager.get_session()
        try:
            clients = session.query(Client).filter(Client.active_status == True).all()
            return clients
        except Exception as e:
            logger.error(f"Error obteniendo clientes: {e}")
            raise
        finally:
            DatabaseManager.close_session(session)
    
    @classmethod
    def get_active_sample_stats(cls):
        """Obtener estadísticas SOLO de muestras activas (active_status = 1)"""
        session = DatabaseManager.get_session()
        try:
            # Total de muestras activas solamente
            total_active = session.query(Sample).filter(Sample.active_status == 1).count()
            
            # Por estado (solo muestras activas)
            extracted = session.query(Sample).filter(
                Sample.active_status == 1, 
                Sample.status == 'EXTRAIDA'
            ).count()
            
            tested = session.query(Sample).filter(
                Sample.active_status == 1, 
                Sample.status == 'ANALIZADA'
            ).count()
            
            stored = session.query(Sample).filter(
                Sample.active_status == 1, 
                Sample.status == 'ALMACENADA'
            ).count()
            
            disposed = session.query(Sample).filter(
                Sample.active_status == 1, 
                Sample.status == 'DEVUELTA'
            ).count()
            
            return {
                'total_active': total_active,
                'extracted': extracted,
                'tested': tested,
                'stored': stored,
                'disposed': disposed
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas activas: {e}")
            return {
                'total_active': 0,
                'extracted': 0, 
                'tested': 0, 
                'stored': 0, 
                'disposed': 0
            }
        finally:
            DatabaseManager.close_session(session)