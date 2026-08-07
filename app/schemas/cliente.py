from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

# 🔹 Base
class ClienteBase(BaseModel):
    nombre: str
    cedula: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    observaciones: Optional[str] = None
    nivel_riesgo: Optional[str] = "Bajo"
    foto_url: Optional[str] = None
    foto_local_path: Optional[str] = None

# 🔹 Crear cliente
class ClienteCreate(ClienteBase):
    class Config:
        extra = "ignore"

# 🔹 Actualizar cliente
class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    cedula: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    observaciones: Optional[str] = None
    nivel_riesgo: Optional[str] = None
    foto_url: Optional[str] = None
    foto_local_path: Optional[str] = None

    class Config:
        extra = "ignore"

# 🔹 Respuesta simplificada para listados
class ClienteResponse(ClienteBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True

# 🔹 Detalle del cliente con sus préstamos
class PrestamoBrief(BaseModel):
    id: int
    monto: float
    fecha_creacion: datetime
    saldo: Optional[Decimal] = None

    class Config:
        from_attributes = True

class ClienteDetail(ClienteResponse):
    prestamos: List[PrestamoBrief] = []