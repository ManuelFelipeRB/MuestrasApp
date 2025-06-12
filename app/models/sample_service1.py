"""
Servicio de gestión de muestras
Lógica de negocio para el CRUD completo de muestras
"""
from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from app.models.database import DatabaseManager
from app.models.sample import Sample
from app.models.batch import Batch
from app.models.client import Client
from app.models.mine import Mine
from app.models.warehouse import Warehouse
from app.models.audit_log import AuditLog

class SampleService:
    """Servicio principal para gestión de muestras"""
    
    @staticmethod
    def generate_sample_code() -> str:
        """Generar código único de muestra"""
        session = DatabaseManager.get_session()
        try:
            # Obtener el último número de muestra
            last_sample = session.query(Sample).order_by(Sample.id.desc()).first()
            if last_sample and last_sample.sample_code.startswith("MUE-"):
                try:
                    last_number = int(last_sample.sample_code.split("-")[1])
                    new_number = last_number + 1
                except:
                    new_number = 1
            else:
                new_number = 1
            
            return f"MUE-{new_number:06d}"  # MUE-000001, MUE-000002, etc.
            
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def create_sample(client_id: int, batch_id: int, warehouse_id: int, 
                     seal_code: str, observations: str, storage_location: str,
                     quantity: float = 0.0, unit: str = "g") -> Dict[str, Any]:
        """
        Crear nueva muestra
        Estado inicial: 'CUSTODY' (Muestra en Custodia)
        """
        session = DatabaseManager.get_session()
        try:
            # Generar código único
            sample_code = SampleService.generate_sample_code()
            
            # Verificar que existen los registros referenciados
            batch = session.query(Batch).get(batch_id)
            if not batch:
                return {"success": False, "error": "Lote no encontrado"}
            
            warehouse = session.query(Warehouse).get(warehouse_id)
            if not warehouse:
                return {"success": False, "error": "Bodega no encontrada"}
            
            # Crear muestra
            sample = Sample(
                batch_id=batch_id,
                sample_code=sample_code,
                description=f"Muestra {seal_code} - Cliente ID: {client_id}",
                extraction_date=date.today(),
                quantity=quantity,
                unit=unit,
                status="CUSTODY",  # Estado inicial
                lab_notes=f"Sello: {seal_code}\nUbicación: {storage_location}\nObservaciones: {observations}",
                active_status=True
            )
            
            # Agregar campos personalizados (los agregaremos al modelo después)
            sample.client_id = client_id
            sample.warehouse_id = warehouse_id
            sample.seal_code = seal_code
            sample.storage_location = storage_location
            sample.observations = observations
            
            session.add(sample)
            session.commit()
            
            # Registrar en auditoría
            audit = AuditLog.create_log(
                action="CREATE",
                table_name="samples",
                record_id=sample.id,
                new_values={
                    "sample_code": sample_code,
                    "client_id": client_id,
                    "batch_id": batch_id,
                    "warehouse_id": warehouse_id,
                    "seal_code": seal_code,
                    "status": "CUSTODY"
                },
                summary=f"Nueva muestra en custodia: {sample_code}"
            )
            session.add(audit)
            session.commit()
            
            return {
                "success": True,
                "sample": sample.to_dict(),
                "message": f"Muestra {sample_code} creada exitosamente"
            }
            
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            DatabaseManager.close_session(session)
    
    
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
    def move_sample_to_lab(sample_id: int, lab_notes: str = None) -> Dict[str, Any]:
        """Mover muestra a laboratorio - cambio de estado"""
        session = DatabaseManager.get_session()
        try:
            sample = session.query(Sample).get(sample_id)
            if not sample:
                return {"success": False, "error": "Muestra no encontrada"}
            
            if sample.status != "CUSTODY":
                return {"success": False, "error": f"Muestra debe estar en custodia. Estado actual: {sample.status}"}
            
            old_status = sample.status
            sample.status = "IN_LAB"
            if lab_notes:
                sample.lab_notes = f"{sample.lab_notes or ''}\nEnvío a lab: {lab_notes}".strip()
            
            session.commit()
            
            # Auditoría
            audit = AuditLog.create_log(
                action="UPDATE",
                table_name="samples",
                record_id=sample.id,
                old_values={"status": old_status},
                new_values={"status": "IN_LAB"},
                summary=f"Muestra enviada a laboratorio: {sample.sample_code}"
            )
            session.add(audit)
            session.commit()
            
            return {"success": True, "message": f"Muestra {sample.sample_code} enviada a laboratorio"}
            
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def transfer_sample_warehouse(sample_id: int, new_warehouse_id: int, notes: str = None) -> Dict[str, Any]:
        """Trasladar muestra entre bodegas"""
        session = DatabaseManager.get_session()
        try:
            sample = session.query(Sample).get(sample_id)
            if not sample:
                return {"success": False, "error": "Muestra no encontrada"}
            
            new_warehouse = session.query(Warehouse).get(new_warehouse_id)
            if not new_warehouse:
                return {"success": False, "error": "Bodega destino no encontrada"}
            
            old_warehouse_id = getattr(sample, 'warehouse_id', None)
            sample.warehouse_id = new_warehouse_id
            
            if notes:
                sample.lab_notes = f"{sample.lab_notes or ''}\nTraslado: {notes}".strip()
            
            session.commit()
            
            # Auditoría
            audit = AuditLog.create_log(
                action="UPDATE",
                table_name="samples",
                record_id=sample.id,
                old_values={"warehouse_id": old_warehouse_id},
                new_values={"warehouse_id": new_warehouse_id},
                summary=f"Muestra trasladada de bodega {old_warehouse_id} a {new_warehouse_id}"
            )
            session.add(audit)
            session.commit()
            
            return {"success": True, "message": f"Muestra {sample.sample_code} trasladada exitosamente"}
            
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def mark_sample_analyzed(sample_id: int, test_results: str, lab_notes: str = None) -> Dict[str, Any]:
        """Marcar muestra como analizada"""
        session = DatabaseManager.get_session()
        try:
            sample = session.query(Sample).get(sample_id)
            if not sample:
                return {"success": False, "error": "Muestra no encontrada"}
            
            sample.mark_as_tested(test_results, lab_notes)
            session.commit()
            
            # Auditoría
            audit = AuditLog.create_log(
                action="UPDATE",
                table_name="samples",
                record_id=sample.id,
                old_values={"status": "IN_LAB"},
                new_values={"status": "TESTED", "test_results": test_results},
                summary=f"Muestra analizada: {sample.sample_code}"
            )
            session.add(audit)
            session.commit()
            
            return {"success": True, "message": f"Muestra {sample.sample_code} marcada como analizada"}
            
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def soft_delete_sample(sample_id: int, reason: str = None) -> Dict[str, Any]:
        """Eliminación virtual - cambiar a inactivo"""
        session = DatabaseManager.get_session()
        try:
            sample = session.query(Sample).get(sample_id)
            if not sample:
                return {"success": False, "error": "Muestra no encontrada"}
            
            if not sample.active_status:
                return {"success": False, "error": "Muestra ya está inactiva"}
            
            sample.active_status = False
            sample.status = "INACTIVE"
            if reason:
                sample.lab_notes = f"{sample.lab_notes or ''}\nEliminada: {reason}".strip()
            
            session.commit()
            
            # Auditoría
            audit = AuditLog.create_log(
                action="DELETE",
                table_name="samples",
                record_id=sample.id,
                old_values={"active_status": True},
                new_values={"active_status": False, "status": "INACTIVE"},
                summary=f"Muestra eliminada (soft delete): {sample.sample_code}"
            )
            session.add(audit)
            session.commit()
            
            return {"success": True, "message": f"Muestra {sample.sample_code} eliminada (inactiva)"}
            
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_dropdown_data() -> Dict[str, List[Dict]]:
        """Obtener datos para dropdowns"""
        session = DatabaseManager.get_session()
        try:
            clients = session.query(Client).filter(Client.active_status == True).all()
            batches = session.query(Batch).filter(Batch.active_status == True).all()
            warehouses = session.query(Warehouse).filter(Warehouse.active_status == True).all()
            
            return {
                "clients": [{"id": c.id, "name": c.name, "code": c.code} for c in clients],
                "batches": [{"id": b.id, "name": b.batch_number, "description": b.description} for b in batches],
                "warehouses": [{"id": w.id, "name": w.name, "code": w.code} for w in warehouses]
            }
            
        finally:
            DatabaseManager.close_session(session)
    
    @staticmethod
    def get_sample_audit_history(sample_id: int) -> List[Dict[str, Any]]:
        """Obtener historial de auditoría de una muestra"""
        session = DatabaseManager.get_session()
        try:
            audits = session.query(AuditLog).filter(
                AuditLog.table_name == "samples",
                AuditLog.record_id == sample_id
            ).order_by(AuditLog.timestamp.desc()).all()
            
            return [audit.to_dict() for audit in audits]
            
        finally:
            DatabaseManager.close_session(session)