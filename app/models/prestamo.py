from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Numeric, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from app.database import Base

class Prestamo(Base):
    __tablename__ = "prestamos"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, nullable=True) # Para sync offline
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    
    # Nuevos campos para tasas de interés
    tipo_interes = Column(String, nullable=True) # diaria, semanal, quincenal, mensual, personalizado
    porcentaje_interes = Column(Float, default=0.0)
    monto_total = Column(Numeric(12, 2), nullable=True) # monto original + intereses calculados
    
    frecuencia_pago = Column(String, nullable=False) # diaria, semanal, mensual
    num_cuotas = Column(Integer, nullable=False)
    estado = Column(String, default="pendiente") # pendiente, pagado
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    cliente = relationship("Cliente", back_populates="prestamos")
    cuotas = relationship("Cuota", back_populates="prestamo", cascade="all, delete")
    pagos = relationship("Pago", back_populates="prestamo", cascade="all, delete")

    @property
    def saldo(self) -> Decimal:
        total_pagado = sum((p.monto or Decimal('0.00')) for p in self.pagos)
        # Usar monto_total (con intereses) si existe, sino caer en monto base
        referencia = self.monto_total if self.monto_total else self.monto
        monto_ref = Decimal(str(referencia or Decimal('0.00')))
        return monto_ref - total_pagado