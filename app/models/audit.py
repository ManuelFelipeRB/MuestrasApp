"""
Modelo de Auditoría para el sistema de inventario
Registra todos los cambios y movimientos en el sistema
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base
import json

class AuditLog(Base):
    """
    Modelo de Log de Auditoría
    Registra todos los cambios en el sistema para trazabilidad completa
    """
    __tablename__ = "audit_logs"
    
    # Campos principales
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(50), nullable=False, index=True)  # Tabla afectada
    record_id = Column(Integer, nullable=False, index=True)  # ID del registro afectado
    user_name = Column(String(100), nullable=False, index=True)  # Usuario que realizó la acción
    action_type = Column(String(20), nullable=False, index=True)  # CREATE, UPDATE, DELETE, MOVE, RESTORE
    old_values = Column(JSON)  # Valores anteriores (JSON)
    new_values = Column(JSON)  # Valores nuevos (JSON)
    
    # Campos específicos para movimientos de bodega
    warehouse_from_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    warehouse_to_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    quantity_changed = Column(Float)  # Cantidad involucrada en el cambio
    
    # Campos adicionales
    description = Column(Text)  # Descripción del cambio
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Relaciones
    warehouse_from = relationship(
        "Warehouse", 
        foreign_keys=[warehouse_from_id],
        back_populates="audit_from"
    )
    warehouse_to = relationship(
        "Warehouse",
        foreign_keys=[warehouse_to_id], 
        back_populates="audit_to"
    )
    
    def __repr__(self):
        return f"<AuditLog(table='{self.table_name}', record_id={self.record_id}, action='{self.action_type}', user='{self.user_name}')>"
    
    def __str__(self):
        return f"{self.action_type} en {self.table_name}[{self.record_id}] por {self.user_name}"
    
    @property
    def warehouse_from_code(self):
        """Código de bodega origen"""
        return self.warehouse_from.code if self.warehouse_from else None
    
    @property
    def warehouse_to_code(self):
        """Código de bodega destino"""
        return self.warehouse_to.code if self.warehouse_to else None
    
    @property
    def is_movement(self):
        """Verificar si es un movimiento entre bodegas"""
        return self.action_type == "MOVE" and self.warehouse_from_id and self.warehouse_to_id
    
    @property
    def formatted_timestamp(self):
        """Timestamp formateado para visualización"""
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else ""
    
    def get_old_values_dict(self):
        """Obtener valores anteriores como diccionario"""
        if self.old_values:
            if isinstance(self.old_values, str):
                try:
                    return json.loads(self.old_values)
                except json.JSONDecodeError:
                    return {}
            return self.old_values
        return {}
    
    def get_new_values_dict(self):
        """Obtener valores nuevos como diccionario"""
        if self.new_values:
            if isinstance(self.new_values, str):
                try:
                    return json.loads(self.new_values)
                except json.JSONDecodeError:
                    return {}
            return self.new_values
        return {}
    
    def get_changed_fields(self):
        """Obtener lista de campos que cambiaron"""
        old_values = self.get_old_values_dict()
        new_values = self.get_new_values_dict()
        
        changed_fields = []
        all_keys = set(old_values.keys()) | set(new_values.keys())
        
        for key in all_keys:
            old_val = old_values.get(key)
            new_val = new_values.get(key)
            
            if old_val != new_val:
                changed_fields.append({
                    "field": key,
                    "old_value": old_val,
                    "new_value": new_val
                })
        
        return changed_fields
    
    def get_summary(self):
        """Obtener resumen del cambio para visualización"""
        summary = {
            "action": self.action_type,
            "table": self.table_name,
            "record_id": self.record_id,
            "user": self.user_name,
            "timestamp": self.formatted_timestamp,
            "description": self.description
        }
        
        if self.is_movement:
            summary["movement"] = {
                "from_warehouse": self.warehouse_from_code,
                "to_warehouse": self.warehouse_to_code,
                "quantity": self.quantity_changed
            }
        
        if self.action_type == "UPDATE":
            summary["changed_fields"] = self.get_changed_fields()
        
        return summary
    
    @staticmethod
    def create_log(table_name: str, record_id: int, user_name: str, action_type: str,
                   old_values: dict = None, new_values: dict = None,
                   warehouse_from_id: int = None, warehouse_to_id: int = None,
                   quantity_changed: float = None, description: str = None):
        """Método estático para crear un log de auditoría"""
        return AuditLog(
            table_name=table_name,
            record_id=record_id,
            user_name=user_name,
            action_type=action_type,
            old_values=old_values,
            new_values=new_values,
            warehouse_from_id=warehouse_from_id,
            warehouse_to_id=warehouse_to_id,
            quantity_changed=quantity_changed,
            description=description
        )
    
    def to_dict(self):
        """Convertir a diccionario para serialización"""
        return {
            "id": self.id,
            "table_name": self.table_name,
            "record_id": self.record_id,
            "user_name": self.user_name,
            "action_type": self.action_type,
            "old_values": self.get_old_values_dict(),
            "new_values": self.get_new_values_dict(),
            "warehouse_from_id": self.warehouse_from_id,
            "warehouse_to_id": self.warehouse_to_id,
            "warehouse_from_code": self.warehouse_from_code,
            "warehouse_to_code": self.warehouse_to_code,
            "quantity_changed": self.quantity_changed,
            "description": self.description,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "formatted_timestamp": self.formatted_timestamp,
            "is_movement": self.is_movement,
            "summary": self.get_summary()
        }