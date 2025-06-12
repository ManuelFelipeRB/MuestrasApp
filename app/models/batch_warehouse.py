"""
Modelo de relación Lote-Bodega para el sistema de inventario
Permite que un lote se almacene en múltiples bodegas con cantidades específicas
"""
from sqlalchemy import Column, Integer, ForeignKey, Float, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base

class BatchWarehouse(Base):
    """
    Modelo de relación Lote-Bodega (Many-to-Many)
    Permite almacenar cantidades específicas de un lote en diferentes bodegas
    """
    __tablename__ = "batch_warehouses"
    
    # Campos principales
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    
    # Control de cantidades por bodega
    quantity_stored = Column(Float, default=0.0, nullable=False)  # Cantidad almacenada en esta bodega
    notes = Column(Text)  # Notas específicas de almacenamiento
    active_status = Column(Boolean, default=True, nullable=False)
    
    # Campos de auditoría
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones (se configurarán cuando tengamos todos los modelos)
    # batch = relationship("Batch", back_populates="batch_warehouses")
    # warehouse = relationship("Warehouse", back_populates="batch_warehouses")
    
    def __repr__(self):
        return f"<BatchWarehouse(batch_id={self.batch_id}, warehouse_id={self.warehouse_id}, quantity={self.quantity_stored})>"
    
    def __str__(self):
        return f"Lote {self.batch_id} en Bodega {self.warehouse_id}: {self.quantity_stored}kg"
    
    @property
    def batch_number(self):
        """Número del lote"""
        # Temporalmente sin relación directa
        return f"Lote ID: {self.batch_id}"
        # return self.batch.batch_number if self.batch else f"Lote ID: {self.batch_id}"
    
    @property
    def warehouse_code(self):
        """Código de la bodega"""
        # Temporalmente sin relación directa
        return f"W-{self.warehouse_id}"
        # return self.warehouse.code if self.warehouse else f"W-{self.warehouse_id}"
    
    @property
    def warehouse_name(self):
        """Nombre de la bodega"""
        # Temporalmente sin relación directa
        return f"Bodega ID: {self.warehouse_id}"
        # return self.warehouse.name if self.warehouse else f"Bodega ID: {self.warehouse_id}"
    
    def can_extract_quantity(self, quantity: float) -> bool:
        """Verificar si se puede extraer una cantidad de esta ubicación"""
        return self.quantity_stored >= quantity
    
    def extract_quantity(self, quantity: float) -> bool:
        """Extraer una cantidad de esta ubicación específica"""
        if self.can_extract_quantity(quantity):
            self.quantity_stored -= quantity
            return True
        return False
    
    def add_quantity(self, quantity: float):
        """Agregar cantidad a esta ubicación"""
        self.quantity_stored += quantity
    
    def to_dict(self, include_relations=False):
        """Convertir a diccionario para serialización"""
        data = {
            "id": self.id,
            "batch_id": self.batch_id,
            "warehouse_id": self.warehouse_id,
            "quantity_stored": self.quantity_stored,
            "notes": self.notes,
            "active_status": self.active_status,
            "batch_number": self.batch_number,
            "warehouse_code": self.warehouse_code,
            "warehouse_name": self.warehouse_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            # Temporalmente vacío hasta configurar las relaciones
            data["batch"] = None
            data["warehouse"] = None
            
        return data