"""
Servicio para gestión de minas
"""
from typing import List, Optional
from app.models.database import DatabaseManager
from app.models.mine import Mine
from app.models.client import Client
from app.models.audit_log import AuditLog

class MineService:
    
    @staticmethod
    def get_all_mines() -> List[Mine]:
        """Obtener todas las minas"""
        session = DatabaseManager.get_session()
        try:
            mines = session.query(Mine).order_by(Mine.name).all()
            return mines
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_mine_by_id(mine_id: int) -> Optional[Mine]:
        """Obtener mina por ID"""
        session = DatabaseManager.get_session()
        try:
            return session.query(Mine).filter(Mine.id == mine_id).first()
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_mine_by_code(code: str) -> Optional[Mine]:
        """Obtener mina por código"""
        session = DatabaseManager.get_session()
        try:
            return session.query(Mine).filter(Mine.code == code).first()
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_mines_by_client(client_id: int) -> List[Mine]:
        """Obtener minas por cliente"""
        session = DatabaseManager.get_session()
        try:
            mines = session.query(Mine).filter(Mine.client_id == client_id).order_by(Mine.name).all()
            return mines
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def create_mine(mine_data: dict) -> Mine:
        """Crear nueva mina"""
        session = DatabaseManager.get_session()
        try:
            # Verificar que el código no exista
            existing = session.query(Mine).filter(Mine.code == mine_data['code']).first()
            if existing:
                raise ValueError(f"Ya existe una mina con código '{mine_data['code']}'")
            
            # Verificar que el cliente exista
            client = session.query(Client).filter(Client.id == mine_data['client_id']).first()
            if not client:
                raise ValueError(f"Cliente con ID {mine_data['client_id']} no encontrado")
            
            # Crear mina
            mine = Mine(
                name=mine_data['name'],
                code=mine_data['code'],
                location=mine_data.get('location'),
                description=mine_data.get('description'),
                client_id=mine_data['client_id'],
                coordinates=mine_data.get('coordinates'),
                altitude=mine_data.get('altitude'),
                mineral_type=mine_data.get('mineral_type'),
                operational_status=mine_data.get('operational_status', 'ACTIVE'),
                notes=mine_data.get('notes')
            )
            
            session.add(mine)
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="CREATE",
                table_name="mines",
                record_id=mine.id,
                new_values=mine_data,
                summary=f"Mina creada: {mine.name} (Cliente: {client.name})"
            )
            session.add(audit_log)
            session.commit()
            
            return mine
        except Exception as e:
            session.rollback()
            raise e
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def update_mine(mine_id: int, mine_data: dict) -> Mine:
        """Actualizar mina"""
        session = DatabaseManager.get_session()
        try:
            mine = session.query(Mine).filter(Mine.id == mine_id).first()
            if not mine:
                raise ValueError(f"Mina con ID {mine_id} no encontrada")
            
            # Verificar código único si cambió
            if 'code' in mine_data and mine_data['code'] != mine.code:
                existing = session.query(Mine).filter(
                    Mine.code == mine_data['code'],
                    Mine.id != mine_id
                ).first()
                if existing:
                    raise ValueError(f"Ya existe una mina con código '{mine_data['code']}'")
            
            # Verificar cliente si cambió
            if 'client_id' in mine_data and mine_data['client_id'] != mine.client_id:
                client = session.query(Client).filter(Client.id == mine_data['client_id']).first()
                if not client:
                    raise ValueError(f"Cliente con ID {mine_data['client_id']} no encontrado")
            
            # Guardar valores anteriores para auditoría
            old_values = {
                'name': mine.name,
                'code': mine.code,
                'location': mine.location,
                'description': mine.description,
                'client_id': mine.client_id,
                'coordinates': mine.coordinates,
                'altitude': mine.altitude,
                'mineral_type': mine.mineral_type,
                'operational_status': mine.operational_status,
                'notes': mine.notes
            }
            
            # Actualizar campos
            if 'name' in mine_data:
                mine.name = mine_data['name']
            if 'code' in mine_data:
                mine.code = mine_data['code']
            if 'location' in mine_data:
                mine.location = mine_data['location']
            if 'description' in mine_data:
                mine.description = mine_data['description']
            if 'client_id' in mine_data:
                mine.client_id = mine_data['client_id']
            if 'coordinates' in mine_data:
                mine.coordinates = mine_data['coordinates']
            if 'altitude' in mine_data:
                mine.altitude = mine_data['altitude']
            if 'mineral_type' in mine_data:
                mine.mineral_type = mine_data['mineral_type']
            if 'operational_status' in mine_data:
                mine.operational_status = mine_data['operational_status']
            if 'notes' in mine_data:
                mine.notes = mine_data['notes']
            
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="UPDATE",
                table_name="mines",
                record_id=mine.id,
                old_values=old_values,
                new_values=mine_data,
                summary=f"Mina actualizada: {mine.name}"
            )
            session.add(audit_log)
            session.commit()
            
            return mine
        except Exception as e:
            session.rollback()
            raise e
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def delete_mine(mine_id: int) -> bool:
        """Eliminar mina"""
        session = DatabaseManager.get_session()
        try:
            mine = session.query(Mine).filter(Mine.id == mine_id).first()
            if not mine:
                raise ValueError(f"Mina con ID {mine_id} no encontrada")
            
            # Verificar que no tenga lotes asociados
            if mine.batches:
                raise ValueError(f"No se puede eliminar la mina '{mine.name}' porque tiene lotes asociados")
            
            # Guardar datos para auditoría
            mine_data = {
                'name': mine.name,
                'code': mine.code,
                'location': mine.location,
                'client_id': mine.client_id
            }
            
            session.delete(mine)
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="DELETE",
                table_name="mines",
                record_id=mine_id,
                old_values=mine_data,
                summary=f"Mina eliminada: {mine.name}"
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
    def search_mines(search_term: str) -> List[Mine]:
        """Buscar minas por término"""
        session = DatabaseManager.get_session()
        try:
            search_pattern = f"%{search_term}%"
            mines = session.query(Mine).filter(
                (Mine.name.ilike(search_pattern)) |
                (Mine.code.ilike(search_pattern)) |
                (Mine.location.ilike(search_pattern)) |
                (Mine.mineral_type.ilike(search_pattern))
            ).order_by(Mine.name).all()
            return mines
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_mine_statistics(mine_id: int) -> dict:
        """Obtener estadísticas de la mina"""
        session = DatabaseManager.get_session()
        try:
            from app.models.batch import Batch
            from app.models.sample import Sample
            
            mine = session.query(Mine).filter(Mine.id == mine_id).first()
            if not mine:
                raise ValueError(f"Mina con ID {mine_id} no encontrada")
            
            # Contar lotes
            batches_count = session.query(Batch).filter(Batch.mine_id == mine_id).count()
            
            # Contar muestras a través de los lotes
            samples_count = session.query(Sample).join(Batch).filter(Batch.mine_id == mine_id).count()
            
            # Calcular cantidad total de mineral extraído
            total_quantity = session.query(
                session.query(Batch.total_quantity).filter(Batch.mine_id == mine_id).scalar_subquery()
            ).scalar() or 0
            
            return {
                'mine_name': mine.name,
                'batches_count': batches_count,
                'samples_count': samples_count,
                'total_quantity_extracted': total_quantity,
                'operational_status': mine.operational_status
            }
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def update_operational_status(mine_id: int, status: str) -> Mine:
        """Actualizar estado operacional de la mina"""
        valid_statuses = ['ACTIVE', 'INACTIVE', 'MAINTENANCE', 'SUSPENDED']
        if status not in valid_statuses:
            raise ValueError(f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}")
        
        return MineService.update_mine(mine_id, {'operational_status': status})