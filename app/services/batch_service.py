"""
Servicio para gestión de lotes
"""
from typing import List, Optional
from datetime import date
from app.models.database import DatabaseManager
from app.models.batch import Batch
from app.models.mine import Mine
from app.models.warehouse import Warehouse
from app.models.batch_warehouse import BatchWarehouse
from app.models.audit_log import AuditLog

class BatchService:
    
    @staticmethod
    def get_all_batches() -> List[Batch]:
        """Obtener todos los lotes"""
        session = DatabaseManager.get_session()
        try:
            batches = session.query(Batch).order_by(Batch.extraction_date.desc()).all()
            return batches
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_batch_by_id(batch_id: int) -> Optional[Batch]:
        """Obtener lote por ID"""
        session = DatabaseManager.get_session()
        try:
            return session.query(Batch).filter(Batch.id == batch_id).first()
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_batch_by_number(batch_number: str) -> Optional[Batch]:
        """Obtener lote por número"""
        session = DatabaseManager.get_session()
        try:
            return session.query(Batch).filter(Batch.batch_number == batch_number).first()
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_batches_by_mine(mine_id: int) -> List[Batch]:
        """Obtener lotes por mina"""
        session = DatabaseManager.get_session()
        try:
            batches = session.query(Batch).filter(Batch.mine_id == mine_id).order_by(Batch.extraction_date.desc()).all()
            return batches
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def create_batch(batch_data: dict) -> Batch:
        """Crear nuevo lote"""
        session = DatabaseManager.get_session()
        try:
            # Verificar que el número de lote no exista
            existing = session.query(Batch).filter(Batch.batch_number == batch_data['batch_number']).first()
            if existing:
                raise ValueError(f"Ya existe un lote con número '{batch_data['batch_number']}'")
            
            # Verificar que la mina exista
            mine = session.query(Mine).filter(Mine.id == batch_data['mine_id']).first()
            if not mine:
                raise ValueError(f"Mina con ID {batch_data['mine_id']} no encontrada")
            
            # Crear lote
            batch = Batch(
                mine_id=batch_data['mine_id'],
                batch_number=batch_data['batch_number'],
                description=batch_data.get('description'),
                extraction_date=batch_data.get('extraction_date', date.today()),
                total_quantity=batch_data.get('total_quantity', 0.0),
                unit=batch_data.get('unit', 'kg'),
                mineral_type=batch_data.get('mineral_type'),
                grade_estimate=batch_data.get('grade_estimate'),
                location_coords=batch_data.get('location_coords'),
                notes=batch_data.get('notes')
            )
            
            session.add(batch)
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="CREATE",
                table_name="batches",
                record_id=batch.id,
                new_values=batch_data,
                summary=f"Lote creado: {batch.batch_number} (Mina: {mine.name})"
            )
            session.add(audit_log)
            session.commit()
            
            return batch
        except Exception as e:
            session.rollback()
            raise e
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def update_batch(batch_id: int, batch_data: dict) -> Batch:
        """Actualizar lote"""
        session = DatabaseManager.get_session()
        try:
            batch = session.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                raise ValueError(f"Lote con ID {batch_id} no encontrado")
            
            # Verificar número único si cambió
            if 'batch_number' in batch_data and batch_data['batch_number'] != batch.batch_number:
                existing = session.query(Batch).filter(
                    Batch.batch_number == batch_data['batch_number'],
                    Batch.id != batch_id
                ).first()
                if existing:
                    raise ValueError(f"Ya existe un lote con número '{batch_data['batch_number']}'")
            
            # Verificar mina si cambió
            if 'mine_id' in batch_data and batch_data['mine_id'] != batch.mine_id:
                mine = session.query(Mine).filter(Mine.id == batch_data['mine_id']).first()
                if not mine:
                    raise ValueError(f"Mina con ID {batch_data['mine_id']} no encontrada")
            
            # Guardar valores anteriores para auditoría
            old_values = {
                'mine_id': batch.mine_id,
                'batch_number': batch.batch_number,
                'description': batch.description,
                'extraction_date': batch.extraction_date.isoformat() if batch.extraction_date else None,
                'total_quantity': batch.total_quantity,
                'unit': batch.unit,
                'mineral_type': batch.mineral_type,
                'grade_estimate': batch.grade_estimate,
                'location_coords': batch.location_coords,
                'notes': batch.notes
            }
            
            # Actualizar campos
            if 'mine_id' in batch_data:
                batch.mine_id = batch_data['mine_id']
            if 'batch_number' in batch_data:
                batch.batch_number = batch_data['batch_number']
            if 'description' in batch_data:
                batch.description = batch_data['description']
            if 'extraction_date' in batch_data:
                batch.extraction_date = batch_data['extraction_date']
            if 'total_quantity' in batch_data:
                batch.total_quantity = batch_data['total_quantity']
            if 'unit' in batch_data:
                batch.unit = batch_data['unit']
            if 'mineral_type' in batch_data:
                batch.mineral_type = batch_data['mineral_type']
            if 'grade_estimate' in batch_data:
                batch.grade_estimate = batch_data['grade_estimate']
            if 'location_coords' in batch_data:
                batch.location_coords = batch_data['location_coords']
            if 'notes' in batch_data:
                batch.notes = batch_data['notes']
            
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="UPDATE",
                table_name="batches",
                record_id=batch.id,
                old_values=old_values,
                new_values=batch_data,
                summary=f"Lote actualizado: {batch.batch_number}"
            )
            session.add(audit_log)
            session.commit()
            
            return batch
        except Exception as e:
            session.rollback()
            raise e
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def delete_batch(batch_id: int) -> bool:
        """Eliminar lote"""
        session = DatabaseManager.get_session()
        try:
            batch = session.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                raise ValueError(f"Lote con ID {batch_id} no encontrado")
            
            # Verificar que no tenga muestras asociadas
            if batch.samples:
                raise ValueError(f"No se puede eliminar el lote '{batch.batch_number}' porque tiene muestras asociadas")
            
            # Eliminar distribuciones en bodegas
            session.query(BatchWarehouse).filter(BatchWarehouse.batch_id == batch_id).delete()
            
            # Guardar datos para auditoría
            batch_data = {
                'batch_number': batch.batch_number,
                'mine_id': batch.mine_id,
                'total_quantity': batch.total_quantity,
                'extraction_date': batch.extraction_date.isoformat() if batch.extraction_date else None
            }
            
            session.delete(batch)
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="DELETE",
                table_name="batches",
                record_id=batch_id,
                old_values=batch_data,
                summary=f"Lote eliminado: {batch.batch_number}"
            )
            session.add(audit_log)
            session.commit()
            
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def distribute_batch_to_warehouses(batch_id: int, distributions: List[dict]) -> bool:
        """Distribuir lote en bodegas"""
        session = DatabaseManager.get_session()
        try:
            batch = session.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                raise ValueError(f"Lote con ID {batch_id} no encontrado")
            
            # Verificar que las cantidades no excedan el total
            total_distributed = sum(d['quantity'] for d in distributions)
            if total_distributed > batch.total_quantity:
                raise ValueError(f"La cantidad total distribuida ({total_distributed}) excede la cantidad del lote ({batch.total_quantity})")
            
            # Eliminar distribuciones anteriores
            session.query(BatchWarehouse).filter(BatchWarehouse.batch_id == batch_id).delete()
            
            # Crear nuevas distribuciones
            for dist in distributions:
                # Verificar que la bodega exista
                warehouse = session.query(Warehouse).filter(Warehouse.id == dist['warehouse_id']).first()
                if not warehouse:
                    raise ValueError(f"Bodega con ID {dist['warehouse_id']} no encontrada")
                
                batch_warehouse = BatchWarehouse(
                    batch_id=batch_id,
                    warehouse_id=dist['warehouse_id'],
                    quantity_stored=dist['quantity'],
                    storage_date=dist.get('storage_date', date.today()),
                    notes=dist.get('notes')
                )
                session.add(batch_warehouse)
            
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="UPDATE",
                table_name="batch_warehouses",
                record_id=batch_id,
                new_values={'distributions': distributions},
                summary=f"Lote {batch.batch_number} distribuido en {len(distributions)} bodegas"
            )
            session.add(audit_log)
            session.commit()
            
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_batch_distribution(batch_id: int) -> List[BatchWarehouse]:
        """Obtener distribución de un lote en bodegas"""
        session = DatabaseManager.get_session()
        try:
            distributions = session.query(BatchWarehouse).filter(BatchWarehouse.batch_id == batch_id).all()
            return distributions
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def search_batches(search_term: str) -> List[Batch]:
        """Buscar lotes por término"""
        session = DatabaseManager.get_session()
        try:
            search_pattern = f"%{search_term}%"
            batches = session.query(Batch).filter(
                (Batch.batch_number.ilike(search_pattern)) |
                (Batch.description.ilike(search_pattern)) |
                (Batch.mineral_type.ilike(search_pattern))
            ).order_by(Batch.extraction_date.desc()).all()
            return batches
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_batch_statistics(batch_id: int) -> dict:
        """Obtener estadísticas del lote"""
        session = DatabaseManager.get_session()
        try:
            from app.models.sample import Sample
            
            batch = session.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                raise ValueError(f"Lote con ID {batch_id} no encontrado")
            
            # Contar muestras
            samples_count = session.query(Sample).filter(Sample.batch_id == batch_id).count()
            
            # Cantidad total almacenada en bodegas
            distributions = session.query(BatchWarehouse).filter(BatchWarehouse.batch_id == batch_id).all()
            total_stored = sum(d.quantity_stored for d in distributions)
            
            # Cantidad de muestras extraídas
            total_samples_quantity = session.query(
                session.query(Sample.quantity).filter(Sample.batch_id == batch_id).scalar_subquery()
            ).scalar() or 0
            
            return {
                'batch_number': batch.batch_number,
                'total_quantity': batch.total_quantity,
                'total_stored': total_stored,
                'samples_count': samples_count,
                'samples_quantity': total_samples_quantity,
                'warehouses_count': len(distributions),
                'remaining_quantity': batch.total_quantity - total_stored - total_samples_quantity
            }
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_batches_by_date_range(start_date: date, end_date: date) -> List[Batch]:
        """Obtener lotes por rango de fechas"""
        session = DatabaseManager.get_session()
        try:
            batches = session.query(Batch).filter(
                Batch.extraction_date >= start_date,
                Batch.extraction_date <= end_date
            ).order_by(Batch.extraction_date.desc()).all()
            return batches
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def update_quantity(batch_id: int, new_quantity: float) -> Batch:
        """Actualizar cantidad del lote"""
        session = DatabaseManager.get_session()
        try:
            batch = session.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                raise ValueError(f"Lote con ID {batch_id} no encontrado")
            
            # Verificar que la nueva cantidad sea válida
            distributions = session.query(BatchWarehouse).filter(BatchWarehouse.batch_id == batch_id).all()
            total_stored = sum(d.quantity_stored for d in distributions)
            
            if new_quantity < total_stored:
                raise ValueError(f"La nueva cantidad ({new_quantity}) no puede ser menor que la ya almacenada ({total_stored})")
            
            old_quantity = batch.total_quantity
            batch.total_quantity = new_quantity
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="UPDATE",
                table_name="batches",
                record_id=batch.id,
                old_values={'total_quantity': old_quantity},
                new_values={'total_quantity': new_quantity},
                summary=f"Cantidad del lote {batch.batch_number} actualizada de {old_quantity} a {new_quantity}"
            )
            session.add(audit_log)
            session.commit()
            
            return batch
        except Exception as e:
            session.rollback()
            raise e
        finally:
            DatabaseManager.close_session(session)