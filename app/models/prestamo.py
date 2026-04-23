from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Prestamo(Base):
    __tablename__ = "prestamos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    frecuencia_pago = Column(String, nullable=False)  # diaria, semanal, mensual
    num_cuotas = Column(Integer, nullable=False)
    estado = Column(String, default="pendiente") # pendiente, pagado
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    cliente = relationship("Cliente", back_populates="prestamos")
    cuotas = relationship("Cuota", back_populates="prestamo", cascade="all, delete")
    pagos = relationship("Pago", back_populates="prestamo", cascade="all, delete")