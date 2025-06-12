"""
Modelo de Clientes para el sistema de inventario
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base

class Client(Base):
    """
    Modelo de Cliente
    Relaciones: 1:N con Mines (Un cliente puede tener muchas minas)
    """
    __tablename__ = "clients"
    
    # Campos principales
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(20), unique=True, index=True)  # Código único del cliente
    contact_person = Column(String(100))  # Persona de contacto
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    active_status = Column(Boolean, default=True, nullable=False)
    
    # Campos de auditoría
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones (se configurarán cuando tengamos el modelo Mine)
    # mines = relationship("Mine", back_populates="client", lazy="dynamic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Client(name='{self.name}', code='{self.code}')>"
    
    def __str__(self):
        return f"{self.code} - {self.name}" if self.code else self.name
    
    @property
    def total_mines(self):
        """Número total de minas activas del cliente"""
        # Temporalmente retornamos 0 hasta tener el modelo Mine
        return 0
        # return self.mines.filter_by(active_status=True).count()
    
    @property
    def has_active_mines(self):
        """Verificar si el cliente tiene minas activas"""
        return self.total_mines > 0
    
    def can_be_deleted(self):
        """Verificar si el cliente puede ser eliminado (no tiene minas activas)"""
        return not self.has_active_mines
    
    def to_dict(self, include_relations=False):
        """Convertir a diccionario para serialización"""
        data = {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "contact_person": self.contact_person,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "active_status": self.active_status,
            "total_mines": self.total_mines,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            # Temporalmente vacío hasta tener el modelo Mine
            data["mines"] = []
            
        return data