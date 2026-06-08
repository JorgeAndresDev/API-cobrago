from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.cliente import ClienteCreate, ClienteResponse, ClienteDetail, ClienteUpdate
from app.services.cliente_service import crear_cliente, listar_clientes, eliminar_cliente, actualizar_cliente
from app.services.prestamo_service import crear_prestamo
from app.schemas.prestamo import PrestamoCreate, PrestamoResponse
from app.models.cliente import Cliente
from app.auth import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=ClienteResponse)
def create(cliente: ClienteCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    try:
        return crear_cliente(db, **cliente.dict(), usuario_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{cliente_id}", response_model=ClienteResponse)
def update_cliente(
    cliente_id: int, 
    cliente_data: ClienteUpdate, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    try:
        cliente = actualizar_cliente(db, cliente_id, cliente_data.dict(exclude_none=True))
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return cliente
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[ClienteResponse])
def get_all(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return listar_clientes(db)

@router.get("/{cliente_id}", response_model=ClienteDetail)
def get_one(cliente_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@router.post("/{cliente_id}/prestamos", response_model=PrestamoResponse)
def create_prestamo_cliente(cliente_id: int, prestamo: PrestamoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    # Aseguramos que el cliente_id de la URL sea el mismo que el del cuerpo (o lo sobreescribimos)
    prestamo_dict = prestamo.dict()
    prestamo_dict["cliente_id"] = cliente_id
    return crear_prestamo(db, prestamo_dict, usuario_id=current_user.id)

@router.delete("/{cliente_id}")
def delete(cliente_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    cliente = eliminar_cliente(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"message": f"Cliente {cliente_id} eliminado exitosamente"}
