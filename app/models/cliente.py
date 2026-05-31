from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    cedula = Column(String, unique=True, index=True, nullable=False)
    telefono = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    observaciones = Column(Text, nullable=True)
    nivel_riesgo = Column(String, default="Bajo")
    foto_url = Column(String, nullable=True)
    foto_local_path = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    prestamos = relationship("Prestamo", back_populates="cliente", cascade="all, delete")
    usuario = relationship("Usuario", back_populates="clientes")