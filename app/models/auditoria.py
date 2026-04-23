from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from app.database import Base
from datetime import datetime

class HistoriaOperacion(Base):
    __tablename__ = "historial_operaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    accion = Column(String, nullable=False) # "CREAR_PRESTAMO", "PAGO", "CREAR_CLIENTE"
    monto = Column(Numeric(12, 2), nullable=True)
    entidad_id = Column(Integer, nullable=True) # ID de cliente, prestamo o pago
    detalles = Column(String, nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
