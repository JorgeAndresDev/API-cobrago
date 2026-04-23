from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.pago import PagoCreate, PagoResponse
from app.services.pago_service import registrar_pago, listar_pagos
from app.auth import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/pagos", tags=["Pagos"])

@router.post("/", response_model=PagoResponse)
def create_pago(pago: PagoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return registrar_pago(
        db, 
        prestamo_id=pago.prestamo_id, 
        monto=pago.monto, 
        usuario_id=current_user.id,
        comentario=pago.comentario
    )


@router.get("/", response_model=list[PagoResponse])
def get_all(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return listar_pagos(db)
