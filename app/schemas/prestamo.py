from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class CuotaResponse(BaseModel):
    id: int
    numero_cuota: int
    fecha_vencimiento: datetime
    monto_esperado: Decimal
    monto_abonado: Decimal
    estado: str

    class Config:
        from_attributes = True

class PrestamoCreate(BaseModel):
    cliente_id: Optional[int] = None
    monto: Decimal
    frecuencia_pago: str
    num_cuotas: int

class PrestamoResponse(BaseModel):
    id: int
    cliente_id: int
    nombre_cliente: Optional[str] = None
    monto: Decimal
    saldo: Optional[Decimal] = None
    frecuencia_pago: str
    num_cuotas: int
    estado: str
    fecha_creacion: datetime
    cuotas: Optional[List[CuotaResponse]] = []

    class Config:
        from_attributes = True