"""
Modelo temporal simplificado de Bodegas para el sistema de inventario
Versión sin relaciones hacia otros modelos que aún no existen
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.models.database import Base

class Warehouse(Base):
    """
    Modelo temporal de Bodega (sin relaciones)
    Las bodegas son fijas y solo se pueden modificar por código
    """
    __tablename__ = "warehouses"
    
    # Campos principales
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False, index=True)  # W01, W022, etc.
    name = Column(String(100), nullable=False)
    description = Column(Text)
    capacity = Column(Float, default=0.0)  # Capacidad en unidades
    active_status = Column(Boolean, default=True, nullable=False)
    
    # Campos de auditoría
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # NOTA: Las relaciones se agregarán después cuando tengamos todos los modelos
    # batches = relationship("Batch", back_populates="warehouse", lazy="dynamic")
    
    def __repr__(self):
        return f"<Warehouse(code='{self.code}', name='{self.name}')>"
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def to_dict(self):
        """Convertir a diccionario para serialización"""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "capacity": self.capacity,
            "active_status": self.active_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }