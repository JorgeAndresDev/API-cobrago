from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# 🔹 Base
class ClienteBase(BaseModel):
    nombre: str
    cedula: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None

# 🔹 Crear cliente
class ClienteCreate(ClienteBase):
    pass

# 🔹 Respuesta simplificada para listados
class ClienteResponse(ClienteBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True

# 🔹 Detalle del cliente con sus préstamos
class PrestamoBrief(BaseModel):
    id: int
    monto_prestado: float
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class ClienteDetail(ClienteResponse):
    prestamos: List[PrestamoBrief] = []