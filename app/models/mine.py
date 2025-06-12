"""
Modelo de Minas para el sistema de inventario
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base

class Mine(Base):
    """
    Modelo de Mina
    Relaciones: 
    - N:1 con Client (Muchas minas pertenecen a un cliente)
    - 1:N con Batch (Una mina puede tener muchos lotes)
    """
    __tablename__ = "mines"
    
    # Campos principales
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(20), unique=True, index=True)  # Código único de la mina
    location = Column(String(200))  # Ubicación geográfica
    description = Column(Text)
    active_status = Column(Boolean, default=True, nullable=False)
    
    # Relación con Cliente (FK)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False, index=True)
    
    # Campos de auditoría
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones (se configurarán cuando tengamos todos los modelos)
    # client = relationship("Client", back_populates="mines")
    # batches = relationship("Batch", back_populates="mine", lazy="dynamic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Mine(name='{self.name}', code='{self.code}')>"
    
    def __str__(self):
        return f"{self.code} - {self.name}" if self.code else self.name
    
    @property
    def total_batches(self):
        """Número total de lotes activos de la mina"""
        # Temporalmente retornamos 0 hasta tener el modelo Batch
        return 0
        # return self.batches.filter_by(active_status=True).count()
    
    @property
    def has_active_batches(self):
        """Verificar si la mina tiene lotes activos"""
        return self.total_batches > 0
    
    def can_be_deleted(self):
        """Verificar si la mina puede ser eliminada (no tiene lotes activos)"""
        return not self.has_active_batches
    
    @property
    def full_name(self):
        """Nombre completo incluyendo código"""
        return f"{self.code} - {self.name}" if self.code else self.name
    
    def to_dict(self, include_relations=False):
        """Convertir a diccionario para serialización"""
        data = {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "location": self.location,
            "description": self.description,
            "active_status": self.active_status,
            "client_id": self.client_id,
            "total_batches": self.total_batches,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            # Temporalmente vacío hasta configurar las relaciones
            data["client"] = None
            data["batches"] = []
            
        return data