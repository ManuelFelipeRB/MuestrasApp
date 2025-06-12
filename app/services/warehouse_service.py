"""
Servicio para gestión de bodegas
"""
from typing import List, Optional
from app.models.database import DatabaseManager
from app.models.warehouse import Warehouse
from app.models.batch_warehouse import BatchWarehouse
from app.models.sample import Sample
from app.models.audit_log import AuditLog

class WarehouseService:
    
    @staticmethod
    def get_all_warehouses() -> List[Warehouse]:
        """Obtener todas las bodegas"""
        session = DatabaseManager.get_session()
        try:
            warehouses = session.query(Warehouse).order_by(Warehouse.code).all()
            return warehouses
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_warehouse_by_id(warehouse_id: int) -> Optional[Warehouse]:
        """Obtener bodega por ID"""
        session = DatabaseManager.get_session()
        try:
            return session.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_warehouse_by_code(code: str) -> Optional[Warehouse]:
        """Obtener bodega por código"""
        session = DatabaseManager.get_session()
        try:
            return session.query(Warehouse).filter(Warehouse.code == code).first()
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def create_warehouse(warehouse_data: dict) -> Warehouse:
        """Crear nueva bodega"""
        session = DatabaseManager.get_session()
        try:
            # Verificar que el código no exista
            existing = session.query(Warehouse).filter(Warehouse.code == warehouse_data['code']).first()
            if existing:
                raise ValueError(f"Ya existe una bodega con código '{warehouse_data['code']}'")
            
            # Crear bodega
            warehouse = Warehouse(
                name=warehouse_data['name'],
                code=warehouse_data['code'],
                location=warehouse_data.get('location'),
                description=warehouse_data.get('description'),
                capacity=warehouse_data.get('capacity'),
                temperature_controlled=warehouse_data.get('temperature_controlled', False),
                security_level=warehouse_data.get('security_level', 'STANDARD'),
                status=warehouse_data.get('status', 'ACTIVE'),
                notes=warehouse_data.get('notes')
            )
            
            session.add(warehouse)
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="CREATE",
                table_name="warehouses",
                record_id=warehouse.id,
                new_values=warehouse_data,
                summary=f"Bodega creada: {warehouse.name} ({warehouse.code})"
            )
            session.add(audit_log)
            session.commit()
            
            return warehouse
        except Exception as e:
            session.rollback()
            raise e
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def update_warehouse(warehouse_id: int, warehouse_data: dict) -> Warehouse:
        """Actualizar bodega"""
        session = DatabaseManager.get_session()
        try:
            warehouse = session.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if not warehouse:
                raise ValueError(f"Bodega con ID {warehouse_id} no encontrada")
            
            # Verificar código único si cambió
            if 'code' in warehouse_data and warehouse_data['code'] != warehouse.code:
                existing = session.query(Warehouse).filter(
                    Warehouse.code == warehouse_data['code'],
                    Warehouse.id != warehouse_id
                ).first()
                if existing:
                    raise ValueError(f"Ya existe una bodega con código '{warehouse_data['code']}'")
            
            # Guardar valores anteriores para auditoría
            old_values = {
                'name': warehouse.name,
                'code': warehouse.code,
                'location': warehouse.location,
                'description': warehouse.description,
                'capacity': warehouse.capacity,
                'temperature_controlled': warehouse.temperature_controlled,
                'security_level': warehouse.security_level,
                'status': warehouse.status,
                'notes': warehouse.notes
            }
            
            # Actualizar campos
            if 'name' in warehouse_data:
                warehouse.name = warehouse_data['name']
            if 'code' in warehouse_data:
                warehouse.code = warehouse_data['code']
            if 'location' in warehouse_data:
                warehouse.location = warehouse_data['location']
            if 'description' in warehouse_data:
                warehouse.description = warehouse_data['description']
            if 'capacity' in warehouse_data:
                warehouse.capacity = warehouse_data['capacity']
            if 'temperature_controlled' in warehouse_data:
                warehouse.temperature_controlled = warehouse_data['temperature_controlled']
            if 'security_level' in warehouse_data:
                warehouse.security_level = warehouse_data['security_level']
            if 'status' in warehouse_data:
                warehouse.status = warehouse_data['status']
            if 'notes' in warehouse_data:
                warehouse.notes = warehouse_data['notes']
            
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="UPDATE",
                table_name="warehouses",
                record_id=warehouse.id,
                old_values=old_values,
                new_values=warehouse_data,
                summary=f"Bodega actualizada: {warehouse.name}"
            )
            session.add(audit_log)
            session.commit()
            
            return warehouse
        except Exception as e:
            session.rollback()
            raise e
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def delete_warehouse(warehouse_id: int) -> bool:
        """Eliminar bodega"""
        session = DatabaseManager.get_session()
        try:
            warehouse = session.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if not warehouse:
                raise ValueError(f"Bodega con ID {warehouse_id} no encontrada")
            
            # Verificar que no tenga lotes almacenados
            batch_count = session.query(BatchWarehouse).filter(BatchWarehouse.warehouse_id == warehouse_id).count()
            if batch_count > 0:
                raise ValueError(f"No se puede eliminar la bodega '{warehouse.name}' porque tiene {batch_count} lotes almacenados")
            
            # Verificar que no tenga muestras almacenadas
            sample_count = session.query(Sample).filter(Sample.warehouse_id == warehouse_id).count()
            if sample_count > 0:
                raise ValueError(f"No se puede eliminar la bodega '{warehouse.name}' porque tiene {sample_count} muestras almacenadas")
            
            # Guardar datos para auditoría
            warehouse_data = {
                'name': warehouse.name,
                'code': warehouse.code,
                'location': warehouse.location,
                'capacity': warehouse.capacity
            }
            
            session.delete(warehouse)
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="DELETE",
                table_name="warehouses",
                record_id=warehouse_id,
                old_values=warehouse_data,
                summary=f"Bodega eliminada: {warehouse.name}"
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
    def get_warehouse_contents(warehouse_id: int) -> dict:
        """Obtener contenido de una bodega"""
        session = DatabaseManager.get_session()
        try:
            warehouse = session.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if not warehouse:
                raise ValueError(f"Bodega con ID {warehouse_id} no encontrada")
            
            # Obtener lotes almacenados
            batch_warehouses = session.query(BatchWarehouse).filter(BatchWarehouse.warehouse_id == warehouse_id).all()
            
            # Obtener muestras almacenadas
            samples = session.query(Sample).filter(Sample.warehouse_id == warehouse_id).all()
            
            # Calcular totales
            total_batch_quantity = sum(bw.quantity_stored for bw in batch_warehouses)
            total_sample_quantity = sum(s.quantity for s in samples)
            
            return {
                'warehouse': warehouse,
                'batches': batch_warehouses,
                'samples': samples,
                'total_batch_quantity': total_batch_quantity,
                'total_sample_quantity': total_sample_quantity,
                'total_items': len(batch_warehouses) + len(samples)
            }
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_warehouse_utilization(warehouse_id: int) -> dict:
        """Obtener utilización de la bodega"""
        session = DatabaseManager.get_session()
        try:
            warehouse = session.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if not warehouse:
                raise ValueError(f"Bodega con ID {warehouse_id} no encontrada")
            
            contents = WarehouseService.get_warehouse_contents(warehouse_id)
            
            total_stored = contents['total_batch_quantity'] + contents['total_sample_quantity']
            utilization_percentage = 0
            
            if warehouse.capacity:
                utilization_percentage = (total_stored / warehouse.capacity) * 100
            
            return {
                'warehouse_name': warehouse.name,
                'capacity': warehouse.capacity,
                'total_stored': total_stored,
                'available_space': warehouse.capacity - total_stored if warehouse.capacity else None,
                'utilization_percentage': utilization_percentage,
                'batch_count': len(contents['batches']),
                'sample_count': len(contents['samples'])
            }
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def search_warehouses(search_term: str) -> List[Warehouse]:
        """Buscar bodegas por término"""
        session = DatabaseManager.get_session()
        try:
            search_pattern = f"%{search_term}%"
            warehouses = session.query(Warehouse).filter(
                (Warehouse.name.ilike(search_pattern)) |
                (Warehouse.code.ilike(search_pattern)) |
                (Warehouse.location.ilike(search_pattern))
            ).order_by(Warehouse.code).all()
            return warehouses
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_available_warehouses() -> List[Warehouse]:
        """Obtener bodegas disponibles (activas)"""
        session = DatabaseManager.get_session()
        try:
            warehouses = session.query(Warehouse).filter(Warehouse.status == 'ACTIVE').order_by(Warehouse.code).all()
            return warehouses
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def update_warehouse_status(warehouse_id: int, status: str) -> Warehouse:
        """Actualizar estado de la bodega"""
        valid_statuses = ['ACTIVE', 'INACTIVE', 'MAINTENANCE', 'FULL']
        if status not in valid_statuses:
            raise ValueError(f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}")
        
        return WarehouseService.update_warehouse(warehouse_id, {'status': status})
    
    @staticmethod
    def get_warehouses_by_security_level(security_level: str) -> List[Warehouse]:
        """Obtener bodegas por nivel de seguridad"""
        session = DatabaseManager.get_session()
        try:
            warehouses = session.query(Warehouse).filter(
                Warehouse.security_level == security_level,
                Warehouse.status == 'ACTIVE'
            ).order_by(Warehouse.code).all()
            return warehouses
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_warehouse_statistics() -> dict:
        """Obtener estadísticas generales de bodegas"""
        session = DatabaseManager.get_session()
        try:
            # Contar bodegas por estado
            total_warehouses = session.query(Warehouse).count()
            active_warehouses = session.query(Warehouse).filter(Warehouse.status == 'ACTIVE').count()
            
            # Calcular capacidad total
            total_capacity = session.query(
                session.query(Warehouse.capacity).filter(Warehouse.capacity.isnot(None)).scalar_subquery()
            ).scalar() or 0
            
            # Contar contenido total
            total_batches = session.query(BatchWarehouse).count()
            total_samples = session.query(Sample).count()
            
            return {
                'total_warehouses': total_warehouses,
                'active_warehouses': active_warehouses,
                'total_capacity': total_capacity,
                'total_batch_storage_records': total_batches,
                'total_sample_records': total_samples
            }
        finally:
            DatabaseManager.close_session(session)