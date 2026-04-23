from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, String
from sqlalchemy.orm import relationship
from app.database import Base

class Cuota(Base):
    __tablename__ = "cuotas"

    id = Column(Integer, primary_key=True, index=True)

    prestamo_id = Column(Integer, ForeignKey("prestamos.id"), nullable=False)

    numero_cuota = Column(Integer, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)

    monto_esperado = Column(Numeric(12, 2), nullable=False)
    monto_abonado = Column(Numeric(12, 2), default=0)

    estado = Column(String, default="pendiente")  # pendiente, pagada, atrasada

    prestamo = relationship("Prestamo", back_populates="cuotas")