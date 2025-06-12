"""
Servicio para gestión de clientes
"""
from typing import List, Optional
from app.models.database import DatabaseManager
from app.models.client import Client
from app.models.audit_log import AuditLog

class ClientService:
    
    @staticmethod
    def get_all_clients() -> List[Client]:
        """Obtener todos los clientes"""
        session = DatabaseManager.get_session()
        try:
            clients = session.query(Client).order_by(Client.name).all()
            return clients
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_client_by_id(client_id: int) -> Optional[Client]:
        """Obtener cliente por ID"""
        session = DatabaseManager.get_session()
        try:
            return session.query(Client).filter(Client.id == client_id).first()
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_client_by_code(code: str) -> Optional[Client]:
        """Obtener cliente por código"""
        session = DatabaseManager.get_session()
        try:
            return session.query(Client).filter(Client.code == code).first()
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def create_client(client_data: dict) -> Client:
        """Crear nuevo cliente"""
        session = DatabaseManager.get_session()
        try:
            # Verificar que el código no exista
            existing = session.query(Client).filter(Client.code == client_data['code']).first()
            if existing:
                raise ValueError(f"Ya existe un cliente con código '{client_data['code']}'")
            
            # Crear cliente
            client = Client(
                name=client_data['name'],
                code=client_data['code'],
                contact_person=client_data.get('contact_person'),
                email=client_data.get('email'),
                phone=client_data.get('phone'),
                address=client_data.get('address'),
                notes=client_data.get('notes')
            )
            
            session.add(client)
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="CREATE",
                table_name="clients",
                record_id=client.id,
                new_values=client_data,
                summary=f"Cliente creado: {client.name}"
            )
            session.add(audit_log)
            session.commit()
            
            return client
        except Exception as e:
            session.rollback()
            raise e
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def update_client(client_id: int, client_data: dict) -> Client:
        """Actualizar cliente"""
        session = DatabaseManager.get_session()
        try:
            client = session.query(Client).filter(Client.id == client_id).first()
            if not client:
                raise ValueError(f"Cliente con ID {client_id} no encontrado")
            
            # Verificar código único si cambió
            if 'code' in client_data and client_data['code'] != client.code:
                existing = session.query(Client).filter(
                    Client.code == client_data['code'],
                    Client.id != client_id
                ).first()
                if existing:
                    raise ValueError(f"Ya existe un cliente con código '{client_data['code']}'")
            
            # Guardar valores anteriores para auditoría
            old_values = {
                'name': client.name,
                'code': client.code,
                'contact_person': client.contact_person,
                'email': client.email,
                'phone': client.phone,
                'address': client.address,
                'notes': client.notes
            }
            
            # Actualizar campos
            if 'name' in client_data:
                client.name = client_data['name']
            if 'code' in client_data:
                client.code = client_data['code']
            if 'contact_person' in client_data:
                client.contact_person = client_data['contact_person']
            if 'email' in client_data:
                client.email = client_data['email']
            if 'phone' in client_data:
                client.phone = client_data['phone']
            if 'address' in client_data:
                client.address = client_data['address']
            if 'notes' in client_data:
                client.notes = client_data['notes']
            
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="UPDATE",
                table_name="clients",
                record_id=client.id,
                old_values=old_values,
                new_values=client_data,
                summary=f"Cliente actualizado: {client.name}"
            )
            session.add(audit_log)
            session.commit()
            
            return client
        except Exception as e:
            session.rollback()
            raise e
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def delete_client(client_id: int) -> bool:
        """Eliminar cliente"""
        session = DatabaseManager.get_session()
        try:
            client = session.query(Client).filter(Client.id == client_id).first()
            if not client:
                raise ValueError(f"Cliente con ID {client_id} no encontrado")
            
            # Verificar que no tenga minas asociadas
            if client.mines:
                raise ValueError(f"No se puede eliminar el cliente '{client.name}' porque tiene minas asociadas")
            
            # Guardar datos para auditoría
            client_data = {
                'name': client.name,
                'code': client.code,
                'contact_person': client.contact_person,
                'email': client.email
            }
            
            session.delete(client)
            session.commit()
            
            # Crear log de auditoría
            audit_log = AuditLog.create_log(
                action="DELETE",
                table_name="clients",
                record_id=client_id,
                old_values=client_data,
                summary=f"Cliente eliminado: {client.name}"
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
    def search_clients(search_term: str) -> List[Client]:
        """Buscar clientes por término"""
        session = DatabaseManager.get_session()
        try:
            search_pattern = f"%{search_term}%"
            clients = session.query(Client).filter(
                (Client.name.ilike(search_pattern)) |
                (Client.code.ilike(search_pattern)) |
                (Client.contact_person.ilike(search_pattern))
            ).order_by(Client.name).all()
            return clients
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_client_statistics(client_id: int) -> dict:
        """Obtener estadísticas del cliente"""
        session = DatabaseManager.get_session()
        try:
            from app.models.mine import Mine
            from app.models.batch import Batch
            from app.models.sample import Sample
            
            client = session.query(Client).filter(Client.id == client_id).first()
            if not client:
                raise ValueError(f"Cliente con ID {client_id} no encontrado")
            
            # Contar minas
            mines_count = session.query(Mine).filter(Mine.client_id == client_id).count()
            
            # Contar lotes a través de las minas
            batches_count = session.query(Batch).join(Mine).filter(Mine.client_id == client_id).count()
            
            # Contar muestras
            samples_count = session.query(Sample).filter(Sample.client_id == client_id).count()
            
            return {
                'client_name': client.name,
                'mines_count': mines_count,
                'batches_count': batches_count,
                'samples_count': samples_count
            }
        finally:
            DatabaseManager.close_session(session)