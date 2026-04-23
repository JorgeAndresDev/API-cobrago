from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal

class PagoBase(BaseModel):
    prestamo_id: int
    monto: Decimal
    comentario: Optional[str] = None

class PagoCreate(PagoBase):
    pass

class PagoResponse(PagoBase):
    id: int
    fecha_pago: datetime

    class Config:
        from_attributes = True
