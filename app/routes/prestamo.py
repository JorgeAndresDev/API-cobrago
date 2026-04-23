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
    # Si no se envía cliente_id, intentamos obtenerlo del usuario autenticado
    if data.cliente_id is None:
        cliente = db.query(Cliente).filter(Cliente.usuario_id == current_user.id).first()
        if not cliente:
            raise HTTPException(
                status_code=400, 
                detail="No tienes un perfil de cliente asociado. Por favor, crea uno primero."
            )
        data.cliente_id = cliente.id
    
    return crear_prestamo(db, data, usuario_id=current_user.id)


@router.get("/", response_model=list[PrestamoResponse])
def get_all(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return listar_prestamos(db)


@router.delete("/{prestamo_id}")
def delete(prestamo_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    prestamo = eliminar_prestamo(db, prestamo_id)
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return {"message": f"Préstamo {prestamo_id} eliminado exitosamente"}