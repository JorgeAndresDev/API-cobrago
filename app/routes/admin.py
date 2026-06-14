from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.auth import get_admin_user
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.prestamo import Prestamo
from app.models.pago import Pago
from app.schemas.usuario import UsuarioOut, UsuarioAdminUpdate
from typing import List

router = APIRouter(prefix="/admin", tags=["Administración"])

@router.get("/usuarios", response_model=List[UsuarioOut])
def list_users(db: Session = Depends(get_db), admin: Usuario = Depends(get_admin_user)):
    """Lista todos los usuarios del sistema (Acceso Admin)"""
    return db.query(Usuario).all()

@router.patch("/usuarios/{usuario_id}", response_model=UsuarioOut)
def update_user_status(
    usuario_id: int, 
    update_data: UsuarioAdminUpdate, 
    db: Session = Depends(get_db), 
    admin: Usuario = Depends(get_admin_user)
):
    """Actualiza el estado, rol o plan de un usuario"""
    user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    data = update_data.dict(exclude_none=True)
    for key, value in data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.get("/stats")
def get_global_stats(db: Session = Depends(get_db), admin: Usuario = Depends(get_admin_user)):
    """Obtiene estadísticas globales para el Dashboard Admin"""
    total_usuarios = db.query(Usuario).count()
    total_clientes = db.query(Cliente).count()
    total_prestamos = db.query(Prestamo).count()
    
    # Suma total de capital prestado
    total_monto_prestado = db.query(func.sum(Prestamo.monto)).scalar() or 0
    
    # Suma total recaudada (pagos)
    total_recaudado = db.query(func.sum(Pago.monto)).scalar() or 0
    
    # Usuarios por plan
    planes = db.query(Usuario.plan_suscripcion, func.count(Usuario.id)).group_by(Usuario.plan_suscripcion).all()
    stats_planes = {plan: count for plan, count in planes}
    
    # Usuarios por estado
    estados = db.query(Usuario.estado_cuenta, func.count(Usuario.id)).group_by(Usuario.estado_cuenta).all()
    stats_estados = {estado: count for estado, count in estados}

    return {
        "resumen": {
            "total_usuarios": total_usuarios,
            "total_clientes": total_clientes,
            "total_prestamos": total_prestamos,
            "total_capital": float(total_monto_prestado),
            "total_recaudado": float(total_recaudado)
        },
        "suscripciones": stats_planes,
        "estados_usuarios": stats_estados
    }
