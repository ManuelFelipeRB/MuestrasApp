"""
Modelo de Lotes (Batches) para el sistema de inventario
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base

class Batch(Base):
    """
    Modelo de Lote
    Relaciones:
    - N:1 con Mine (Un lote pertenece a una sola mina)
    - N:1 con Warehouse (Un lote se almacena en una sola bodega)
    - 1:N con Sample (Un lote puede tener muchas muestras)
    """
    __tablename__ = "batches"
    
    # Campos principales
    id = Column(Integer, primary_key=True, autoincrement=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False, index=True)
    # REMOVIDO: warehouse_id (ahora es relación M:N a través de BatchWarehouse)
    batch_number = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    extraction_date = Column(Date)  # Fecha de extracción del material
    total_quantity = Column(Float, default=0.0)  # Cantidad total del lote
    # NOTA: remaining_quantity se calcula dinámicamente, no se almacena en BD
    unit = Column(String(10), default="kg")  # Unidad de medida
    active_status = Column(Boolean, default=True, nullable=False)
    
    # Campos de auditoría
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones (se configurarán cuando tengamos todos los modelos)
    # mine = relationship("Mine", back_populates="batches")
    # warehouses = relationship("Warehouse", secondary="batch_warehouses", back_populates="batches")
    # batch_warehouses = relationship("BatchWarehouse", back_populates="batch", cascade="all, delete-orphan")
    # samples = relationship("Sample", back_populates="batch", lazy="dynamic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Batch(number='{self.batch_number}', mine_id={self.mine_id}, total_warehouses={self.total_warehouses})>"
    
    def __str__(self):
        return f"{self.batch_number}"
    
    @property
    def total_warehouses(self):
        """Número total de bodegas donde está almacenado el lote"""
        # Temporalmente retornamos 0 hasta tener el modelo BatchWarehouse
        return 0
        # return len([bw for bw in self.batch_warehouses if bw.active_status and bw.quantity_stored > 0])
    
    @property
    def warehouses_list(self):
        """Lista de bodegas donde está almacenado"""
        # Temporalmente retornamos lista vacía
        return []
        # return [bw.warehouse for bw in self.batch_warehouses if bw.active_status and bw.quantity_stored > 0]
    
    @property
    def stored_quantity(self):
        """Cantidad total almacenada en todas las bodegas"""
        # Temporalmente retornamos total_quantity
        return self.total_quantity or 0.0
        # return sum(bw.quantity_stored for bw in self.batch_warehouses if bw.active_status)
    
    @property
    def remaining_quantity_calculated(self):
        """Cantidad restante disponible (calculada)"""
        # La cantidad restante es la cantidad almacenada menos la usada en muestras
        return self.stored_quantity - self.samples_total_quantity
    def total_samples(self):
        """Número total de muestras activas del lote"""
        # Temporalmente retornamos 0 hasta tener el modelo Sample
        return 0
        # return self.samples.filter_by(active_status=True).count()
    
    @property
    def used_quantity(self):
        """Cantidad utilizada del lote (total - almacenada)"""
        return (self.total_quantity or 0.0) - (self.stored_quantity or 0.0)
    
    @property
    def usage_percentage(self):
        """Porcentaje de uso del lote"""
        if not self.total_quantity or self.total_quantity <= 0:
            return 0.0
        return min((self.used_quantity / self.total_quantity) * 100, 100.0)
    
    @property
    def samples_total_quantity(self):
        """Cantidad total de todas las muestras del lote"""
        # Temporalmente retornamos 0 hasta tener el modelo Sample
        return 0.0
        # total = 0.0
        # for sample in self.samples.filter_by(active_status=True):
        #     if sample.quantity:
        #         total += sample.quantity
        # return total
    
    @property
    def is_depleted(self):
        """Verificar si el lote está agotado"""
        return (self.stored_quantity or 0.0) <= 0
    
    @property
    def has_active_samples(self):
        """Verificar si el lote tiene muestras activas"""
        return self.total_samples > 0
    
    def can_extract_quantity(self, quantity: float) -> bool:
        """Verificar si se puede extraer una cantidad del lote"""
        return (self.remaining_quantity or 0.0) >= quantity
    
    def extract_quantity(self, quantity: float) -> bool:
        """Extraer una cantidad del lote"""
        if self.can_extract_quantity(quantity):
            self.remaining_quantity = (self.remaining_quantity or 0.0) - quantity
            return True
        return False
    
    def restore_quantity(self, quantity: float):
        """Restaurar una cantidad al lote"""
        self.remaining_quantity = (self.remaining_quantity or 0.0) + quantity
        # No permitir que la cantidad restante exceda la total
        if self.total_quantity and self.remaining_quantity > self.total_quantity:
            self.remaining_quantity = self.total_quantity
    
    def get_samples_list(self):
        """Obtener lista de muestras activas"""
        # Temporalmente retornamos lista vacía hasta tener el modelo Sample
        return []
        # return self.samples.filter_by(active_status=True).all()
    
    def can_be_deleted(self):
        """Verificar si el lote puede ser eliminado (no tiene muestras activas)"""
        return not self.has_active_samples
    
    @property
    def mine_name(self):
        """Nombre de la mina"""
        # Temporalmente sin relación directa
        return f"Mina ID: {self.mine_id}"
        # return self.mine.name if self.mine else "Sin mina"
    
    @property
    def client_name(self):
        """Nombre del cliente (a través de la mina)"""
        # Temporalmente sin relación directa
        return "Sin cliente"
        # return self.mine.client.name if self.mine and self.mine.client else "Sin cliente"
    
    @property
    def warehouse_codes(self):
        """Códigos de las bodegas donde está almacenado"""
        # Temporalmente sin relación directa
        return "Sin bodegas"
        # return ", ".join([bw.warehouse.code for bw in self.batch_warehouses if bw.active_status and bw.quantity_stored > 0])
    
    @property
    def warehouse_names(self):
        """Nombres de las bodegas donde está almacenado"""
        # Temporalmente sin relación directa
        return "Sin bodegas"
        # return ", ".join([bw.warehouse.name for bw in self.batch_warehouses if bw.active_status and bw.quantity_stored > 0])
    
    def get_warehouse_distribution(self):
        """Obtener distribución de cantidades por bodega"""
        # Temporalmente retornamos lista vacía
        return []
        # return [
        #     {
        #         "warehouse_code": bw.warehouse.code,
        #         "warehouse_name": bw.warehouse.name,
        #         "quantity_stored": bw.quantity_stored,
        #         "notes": bw.notes
        #     }
        #     for bw in self.batch_warehouses 
        #     if bw.active_status and bw.quantity_stored > 0
        # ]
    
    def can_extract_quantity(self, quantity: float, warehouse_id: int = None) -> bool:
        """Verificar si se puede extraer una cantidad del lote"""
        if warehouse_id:
            # Verificar en bodega específica
            # Temporalmente retornamos False
            return False
            # batch_warehouse = next((bw for bw in self.batch_warehouses 
            #                        if bw.warehouse_id == warehouse_id and bw.active_status), None)
            # return batch_warehouse and batch_warehouse.can_extract_quantity(quantity)
        else:
            # Verificar en total
            return self.stored_quantity >= quantity
    
    def extract_quantity(self, quantity: float, warehouse_id: int = None) -> bool:
        """Extraer una cantidad del lote"""
        if warehouse_id:
            # Extraer de bodega específica
            # Temporalmente retornamos False
            return False
            # batch_warehouse = next((bw for bw in self.batch_warehouses 
            #                        if bw.warehouse_id == warehouse_id and bw.active_status), None)
            # return batch_warehouse and batch_warehouse.extract_quantity(quantity)
        else:
            # Extraer automáticamente (FIFO, LIFO, o estrategia definida)
            remaining = quantity
            # Lógica temporal
            return False
    
    def to_dict(self, include_relations=False):
        """Convertir a diccionario para serialización"""
        data = {
            "id": self.id,
            "mine_id": self.mine_id,
            "batch_number": self.batch_number,
            "description": self.description,
            "extraction_date": self.extraction_date.isoformat() if self.extraction_date else None,
            "total_quantity": self.total_quantity,
            "stored_quantity": self.stored_quantity,
            "remaining_quantity": self.remaining_quantity_calculated,
            "used_quantity": self.used_quantity,
            "usage_percentage": self.usage_percentage,
            "unit": self.unit,
            "active_status": self.active_status,
            "total_samples": self.total_samples,
            "total_warehouses": self.total_warehouses,
            "samples_total_quantity": self.samples_total_quantity,
            "is_depleted": self.is_depleted,
            "mine_name": self.mine_name,
            "client_name": self.client_name,
            "warehouse_codes": self.warehouse_codes,
            "warehouse_names": self.warehouse_names,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            # Temporalmente vacío hasta configurar las relaciones
            data["mine"] = None
            data["warehouses"] = []
            data["warehouse_distribution"] = self.get_warehouse_distribution()
            data["samples"] = []
            
        return data