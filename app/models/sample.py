"""
Modelo de Muestras para el sistema de inventario
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base

class Sample(Base):
    """
    Modelo de Muestra
    Relaciones:
    - N:1 con Batch (Una muestra pertenece a un solo lote)
    """
    __tablename__ = "samples"
    
    # Campos principales
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    sample_number = Column(String(50), unique=True, nullable=False, index=True)
    weight = Column(Float)  # Peso de la muestra
    quantity = Column(Float)  # Cantidad de la muestra
    unit = Column(String(10), default="kg")  # Unidad de medida
    quality = Column(String(50))  # Calidad de la muestra
    seals = Column(String(100))  # Información de sellos
    operator = Column(String(100))  # Operador responsable
    date_created = Column(Date)  # Fecha de creación de la muestra
    time_created = Column(Time)  # Hora de creación de la muestra
    details = Column(Text)  # Detalles adicionales
    observations = Column(Text)  # Observaciones
    active_status = Column(Boolean, default=True, nullable=False)
    
    # Campos de auditoría
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    batch = relationship("Batch", back_populates="samples")
    
    def __repr__(self):
        return f"<Sample(number='{self.sample_number}', batch='{self.batch.batch_number if self.batch else None}')>"
    
    def __str__(self):
        return f"{self.sample_number} - {self.batch.batch_number if self.batch else 'Sin lote'}"
    
    @property
    def batch_number(self):
        """Número del lote"""
        return self.batch.batch_number if self.batch else "Sin lote"
    
    @property
    def mine_name(self):
        """Nombre de la mina (a través del lote)"""
        return self.batch.mine.name if self.batch and self.batch.mine else "Sin mina"
    
    @property
    def client_name(self):
        """Nombre del cliente (a través del lote y la mina)"""
        if self.batch and self.batch.mine and self.batch.mine.client:
            return self.batch.mine.client.name
        return "Sin cliente"
    
    @property
    def warehouse_code(self):
        """Código de la bodega (a través del lote)"""
        return self.batch.warehouse.code if self.batch and self.batch.warehouse else "Sin bodega"
    
    @property
    def warehouse_name(self):
        """Nombre de la bodega (a través del lote)"""
        return self.batch.warehouse.name if self.batch and self.batch.warehouse else "Sin bodega"
    
    @property
    def mine_code(self):
        """Código de la mina"""
        return self.batch.mine.code if self.batch and self.batch.mine else "Sin código"
    
    @property
    def client_code(self):
        """Código del cliente"""
        if self.batch and self.batch.mine and self.batch.mine.client:
            return self.batch.mine.client.code
        return "Sin código"
    
    @property
    def full_hierarchy(self):
        """Jerarquía completa: Cliente → Mina → Lote → Muestra"""
        return {
            "client": {
                "id": self.batch.mine.client.id if self.batch and self.batch.mine and self.batch.mine.client else None,
                "name": self.client_name,
                "code": self.client_code
            },
            "mine": {
                "id": self.batch.mine.id if self.batch and self.batch.mine else None,
                "name": self.mine_name,
                "code": self.mine_code
            },
            "batch": {
                "id": self.batch.id if self.batch else None,
                "number": self.batch_number
            },
            "warehouse": {
                "id": self.batch.warehouse.id if self.batch and self.batch.warehouse else None,
                "code": self.warehouse_code,
                "name": self.warehouse_name
            }
        }
    
    @property
    def datetime_created(self):
        """Fecha y hora combinadas de creación"""
        if self.date_created and self.time_created:
            from datetime import datetime, time
            return datetime.combine(self.date_created, self.time_created)
        elif self.date_created:
            return self.date_created
        return None
    
    def update_batch_quantity(self, old_quantity: float = None):
        """Actualizar la cantidad restante del lote al cambiar la muestra"""
        if not self.batch:
            return
        
        # Si es una muestra nueva
        if old_quantity is None and self.quantity:
            self.batch.extract_quantity(self.quantity)
        
        # Si se modificó la cantidad
        elif old_quantity is not None and self.quantity:
            difference = self.quantity - old_quantity
            if difference > 0:
                # Se aumentó la cantidad de la muestra
                self.batch.extract_quantity(difference)
            elif difference < 0:
                # Se disminuyó la cantidad de la muestra
                self.batch.restore_quantity(abs(difference))
    
    def restore_to_batch(self):
        """Restaurar la cantidad de la muestra al lote (al eliminar la muestra)"""
        if self.batch and self.quantity:
            self.batch.restore_quantity(self.quantity)
    
    def can_be_created(self) -> tuple[bool, str]:
        """Verificar si la muestra puede ser creada"""
        if not self.batch:
            return False, "No se ha especificado un lote"
        
        if not self.batch.active_status:
            return False, "El lote no está activo"
        
        if self.quantity and not self.batch.can_extract_quantity(self.quantity):
            return False, f"Cantidad insuficiente en el lote. Disponible: {self.batch.remaining_quantity} {self.batch.unit}"
        
        return True, "OK"
    
    def to_dict(self, include_relations=False):
        """Convertir a diccionario para serialización"""
        data = {
            "id": self.id,
            "batch_id": self.batch_id,
            "sample_number": self.sample_number,
            "weight": self.weight,
            "quantity": self.quantity,
            "unit": self.unit,
            "quality": self.quality,
            "seals": self.seals,
            "operator": self.operator,
            "date_created": self.date_created.isoformat() if self.date_created else None,
            "time_created": self.time_created.isoformat() if self.time_created else None,
            "datetime_created": self.datetime_created.isoformat() if self.datetime_created else None,
            "details": self.details,
            "observations": self.observations,
            "active_status": self.active_status,
            "batch_number": self.batch_number,
            "mine_name": self.mine_name,
            "client_name": self.client_name,
            "warehouse_code": self.warehouse_code,
            "warehouse_name": self.warehouse_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            data["batch"] = self.batch.to_dict() if self.batch else None
            data["full_hierarchy"] = self.full_hierarchy
            
        return data