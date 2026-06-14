from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True)
    
    # Nuevos campos administrativos
    rol = Column(String(20), default="cobrador") # admin, cobrador
    estado_cuenta = Column(String(20), default="activo") # activo, suspendido, inactivo
    plan_suscripcion = Column(String(20), default="basico") # basico, premium, profesional

    # Relación: Si se elimina el usuario, se eliminan todos sus clientes asociados
    clientes = relationship("Cliente", back_populates="usuario", cascade="all, delete-orphan")