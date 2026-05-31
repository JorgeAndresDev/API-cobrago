from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from decimal import Decimal

from app.database import get_db
from app.models.cliente import Cliente
from app.models.prestamo import Prestamo
from app.models.pago import Pago
from app.models.cuota import Cuota
from app.models.usuario import Usuario
from app.auth import get_current_user

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    # 1. Total cartera activa (suma de saldos de préstamos no pagados)
    prestamos_activos_q = db.query(Prestamo).join(Cliente).filter(
        Cliente.usuario_id == current_user.id,
        Prestamo.estado != "pagado"
    ).all()

    cartera_activa = Decimal('0.00')
    for prestamo in prestamos_activos_q:
        cartera_activa += sum((c.monto_esperado or Decimal('0.00')) - (c.monto_abonado or Decimal('0.00')) for c in prestamo.cuotas)

    # 2. Recaudado hoy
    from datetime import datetime
    hoy_inicio = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    pagos_hoy = db.query(Pago).filter(Pago.fecha_pago >= hoy_inicio).all()
    recaudado_hoy = sum((p.monto or Decimal('0.00')) for p in pagos_hoy)

    total_clientes = db.query(func.count(Cliente.id)).filter(Cliente.usuario_id == current_user.id).scalar() or 0
    prestamos_activos = db.query(func.count(Prestamo.id)).join(Cliente).filter(
        Cliente.usuario_id == current_user.id,
        Prestamo.estado != "pagado"
    ).scalar() or 0
    clientes_mora = db.query(func.count(func.distinct(Cliente.id))).join(Prestamo).join(Cuota).filter(
        Cliente.usuario_id == current_user.id,
        Cuota.estado == "atrasada"
    ).scalar() or 0
    cobros_hoy = db.query(func.count(Pago.id)).filter(Pago.fecha_pago >= hoy_inicio).scalar() or 0

    return {
        "recaudado_hoy": recaudado_hoy,
        "cartera_activa": cartera_activa,
        "total_clientes": total_clientes,
        "prestamos_activos": prestamos_activos,
        "clientes_mora": clientes_mora,
        "cobros_hoy": cobros_hoy,
    }
