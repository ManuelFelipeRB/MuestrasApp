"""
Modelo de Muestras para el sistema de inventario
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base

class Sample(Base):
    """
    Modelo de Muestra
    Relaciones:
    - N:1 con Batch (Una muestra pertenece a un lote)
    """
    __tablename__ = "samples"
    
    # Campos principales
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    sample_code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    extraction_date = Column(Date)  # Fecha de extracción de la muestra
    quantity = Column(Float, default=0.0)  # Cantidad de la muestra
    unit = Column(String(10), default="g")  # Unidad de medida (gramos por defecto)
    
    # Estado de la muestra
    status = Column(String(20), default="EXTRACTED")  # EXTRACTED, TESTED, DESTROYED, STORED
    
    # Información de laboratorio
    lab_notes = Column(Text)  # Notas del laboratorio
    test_results = Column(Text)  # Resultados de pruebas (JSON o texto)
    tested_date = Column(Date)  # Fecha de análisis
    
    # Control
    active_status = Column(Boolean, default=True, nullable=False)
    
    # Campos de auditoría
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones (se configurarán cuando tengamos todos los modelos)
    # batch = relationship("Batch", back_populates="samples")
    
    def __repr__(self):
        return f"<Sample(code='{self.sample_code}', batch_id={self.batch_id}, quantity={self.quantity})>"
    
    def __str__(self):
        return f"{self.sample_code} - {self.quantity}{self.unit}"
    
    @property
    def batch_number(self):
        """Número del lote"""
        return f"Lote ID: {self.batch_id}"
        # return self.batch.batch_number if self.batch else f"Lote ID: {self.batch_id}"
    
    @property
    def mine_name(self):
        """Nombre de la mina (a través del lote)"""
        return "Sin mina"
        # return self.batch.mine_name if self.batch else "Sin mina"
    
    @property
    def client_name(self):
        """Nombre del cliente (a través del lote y mina)"""
        return "Sin cliente"
        # return self.batch.client_name if self.batch else "Sin cliente"
    
    @property
    def is_tested(self):
        """Verificar si la muestra fue analizada"""
        return self.status in ["TESTED", "DESTROYED"] and self.tested_date is not None
    
    @property
    def is_active(self):
        """Verificar si la muestra está activa"""
        return self.active_status and self.status not in ["DESTROYED"]
    
    @property
    def days_since_extraction(self):
        """Días desde la extracción"""
        if not self.extraction_date:
            return None
        from datetime import date
        return (date.today() - self.extraction_date).days
    
    @property
    def days_since_test(self):
        """Días desde el análisis"""
        if not self.tested_date:
            return None
        from datetime import date
        return (date.today() - self.tested_date).days
    
    def mark_as_tested(self, test_results: str = None, lab_notes: str = None):
        """Marcar muestra como analizada"""
        from datetime import date
        self.status = "TESTED"
        self.tested_date = date.today()
        if test_results:
            self.test_results = test_results
        if lab_notes:
            self.lab_notes = lab_notes
    
    def mark_as_destroyed(self, reason: str = None):
        """Marcar muestra como destruida"""
        self.status = "DESTROYED"
        if reason:
            self.lab_notes = f"{self.lab_notes or ''}\nDestruida: {reason}".strip()
    
    def can_be_deleted(self):
        """Verificar si la muestra puede ser eliminada"""
        return self.status == "DESTROYED" or not self.is_tested
    
    def to_dict(self, include_relations=False):
        """Convertir a diccionario para serialización"""
        data = {
            "id": self.id,
            "batch_id": self.batch_id,
            "sample_code": self.sample_code,
            "description": self.description,
            "extraction_date": self.extraction_date.isoformat() if self.extraction_date else None,
            "quantity": self.quantity,
            "unit": self.unit,
            "status": self.status,
            "lab_notes": self.lab_notes,
            "test_results": self.test_results,
            "tested_date": self.tested_date.isoformat() if self.tested_date else None,
            "active_status": self.active_status,
            "is_tested": self.is_tested,
            "is_active": self.is_active,
            "days_since_extraction": self.days_since_extraction,
            "days_since_test": self.days_since_test,
            "batch_number": self.batch_number,
            "mine_name": self.mine_name,
            "client_name": self.client_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            data["batch"] = None  # Configurar cuando tengamos las relaciones
            
        return data