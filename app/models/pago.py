from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    prestamo_id = Column(Integer, ForeignKey("prestamos.id"), nullable=False)
    
    monto = Column(Numeric(12, 2), nullable=False)
    fecha_pago = Column(DateTime, default=datetime.utcnow)
    comentario = Column(String, nullable=True)

    # 🔗 Relación
    prestamo = relationship("Prestamo", back_populates="pagos")
