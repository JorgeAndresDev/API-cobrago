from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.prestamo import PrestamoCreate, PrestamoResponse
from app.services.prestamo_service import crear_prestamo, listar_prestamos, eliminar_prestamo
from app.auth import get_current_user
from app.models.usuario import Usuario
from app.models.cliente import Cliente

router = APIRouter(prefix="/prestamos", tags=["Prestamos"])


@router.post("/", response_model=PrestamoResponse)
def create(data: PrestamoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    try:
        return crear_prestamo(db, data, user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[PrestamoResponse])
def get_all(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return listar_prestamos(db, current_user)


@router.delete("/{prestamo_id}")
def delete(prestamo_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    try:
        prestamo = eliminar_prestamo(db, prestamo_id, current_user)
        if not prestamo:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        return {"message": f"Préstamo {prestamo_id} eliminado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))