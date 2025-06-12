"""
Modelo de Auditoría para el sistema de inventario
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.models.database import Base

class AuditLog(Base):
    """
    Modelo de Registro de Auditoría
    Registra todos los cambios importantes en el sistema
    """
    __tablename__ = "audit_logs"
    
    # Campos principales
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Información de la acción
    action = Column(String(20), nullable=False, index=True)  # CREATE, UPDATE, DELETE
    table_name = Column(String(50), nullable=False, index=True)  # Tabla afectada
    record_id = Column(Integer, nullable=False, index=True)  # ID del registro afectado
    
    # Datos del cambio
    old_values = Column(JSON)  # Valores anteriores
    new_values = Column(JSON)  # Valores nuevos
    changes_summary = Column(Text)  # Resumen legible de los cambios
    
    # Información del usuario (futuro)
    user_name = Column(String(100), default="SYSTEM")  # Usuario que hizo el cambio
    
    # Metadatos
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)
    ip_address = Column(String(45))  # IPv4 o IPv6
    user_agent = Column(Text)  # Información del navegador/aplicación
    
    def __repr__(self):
        return f"<AuditLog(action='{self.action}', table='{self.table_name}', record_id={self.record_id})>"
    
    def __str__(self):
        return f"{self.action} en {self.table_name}[{self.record_id}] - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @property
    def formatted_timestamp(self):
        """Timestamp formateado para visualización"""
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
    
    @property
    def action_description(self):
        """Descripción legible de la acción"""
        descriptions = {
            "CREATE": "Creado",
            "UPDATE": "Actualizado", 
            "DELETE": "Eliminado",
            "RESTORE": "Restaurado"
        }
        return descriptions.get(self.action, self.action)
    
    @classmethod
    def create_log(cls, action: str, table_name: str, record_id: int, 
                   old_values: dict = None, new_values: dict = None, 
                   summary: str = None, user_name: str = "SYSTEM"):
        """Crear un nuevo registro de auditoría"""
        
        # Generar resumen automático si no se proporciona
        if not summary:
            if action == "CREATE":
                summary = f"Nuevo registro creado en {table_name}"
            elif action == "UPDATE":
                changes = []
                if old_values and new_values:
                    for key, new_val in new_values.items():
                        old_val = old_values.get(key)
                        if old_val != new_val:
                            changes.append(f"{key}: '{old_val}' → '{new_val}'")
                summary = f"Campos modificados: {', '.join(changes)}" if changes else "Registro actualizado"
            elif action == "DELETE":
                summary = f"Registro eliminado de {table_name}"
            else:
                summary = f"Acción {action} en {table_name}"
        
        return cls(
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            changes_summary=summary,
            user_name=user_name
        )
    
    def to_dict(self):
        """Convertir a diccionario para serialización"""
        return {
            "id": self.id,
            "action": self.action,
            "action_description": self.action_description,
            "table_name": self.table_name,
            "record_id": self.record_id,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "changes_summary": self.changes_summary,
            "user_name": self.user_name,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "formatted_timestamp": self.formatted_timestamp,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent
        }