from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from decimal import Decimal

from app.database import get_db
from app.models.prestamo import Prestamo
from app.models.pago import Pago
from app.models.usuario import Usuario
from app.auth import get_current_user

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    # 1. Total Cartera Activa (suma de saldos de préstamos no pagados)
    # Como el saldo se calcula dinámicamente o se puede sumar del monto total restando pagos
    # Por simplicidad, obtenemos préstamos activos y sumamos su saldo
    prestamos_activos = db.query(Prestamo).filter(Prestamo.estado != "pagado").all()
    
    total_cartera = Decimal('0.00')
    for p in prestamos_activos:
        saldo_pendiente = sum((c.monto_esperado or Decimal('0.00')) - (c.monto_abonado or Decimal('0.00')) for c in p.cuotas)
        total_cartera += saldo_pendiente

    # 2. Total Recaudado Hoy
    from datetime import datetime
    hoy_inicio = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    pagos_hoy = db.query(Pago).filter(Pago.fecha_pago >= hoy_inicio).all()
    recaudado_hoy = sum((p.monto or Decimal('0.00')) for p in pagos_hoy)

    return {
        "cartera_activa": total_cartera,
        "recaudado_hoy": recaudado_hoy
    }
