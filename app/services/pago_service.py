from sqlalchemy.orm import Session
from app.models import Prestamo, Cuota, Pago, HistoriaOperacion
from fastapi import HTTPException
from decimal import Decimal

from datetime import datetime, timezone
from app.models.usuario import Usuario

def registrar_pago(db: Session, prestamo_id: int, monto: Decimal, user: Usuario, comentario: str = None):
    # 1️⃣ VALIDACIÓN DE VENCIMIENTO
    if user.fecha_vencimiento and user.fecha_vencimiento.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise ValueError("Su suscripción ha vencido. Por favor, renueve su plan para continuar.")
    # Usamos try/except con rollback para asegurar atomicidad
    try:
        # 1. Buscar el préstamo
        prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
        if not prestamo:
            raise ValueError("Préstamo no encontrado")
        # 2️⃣ VALIDACIÓN DE PROPIEDAD
        if user.rol != "admin" and prestamo.cliente.usuario_id != user.id:
            raise ValueError("No tiene permisos para registrar pagos en este préstamo.")

        if monto <= 0:
            raise ValueError("El monto debe ser mayor a cero")

        # 2. Obtener cuotas pendientes o parciales ordenadas por fecha
        cuotas_pendientes = db.query(Cuota).filter(
            Cuota.prestamo_id == prestamo_id,
            Cuota.estado != "pagada"
        ).order_by(Cuota.fecha_vencimiento.asc()).all()

        if not cuotas_pendientes:
            raise HTTPException(status_code=400, detail="Este préstamo no tiene cuotas pendientes")

        # 3. Validar que el pago no exceda el saldo pendiente total
        total_pendiente = sum(Decimal(str(c.monto_esperado)) - Decimal(str(c.monto_abonado)) for c in cuotas_pendientes)
        
        if monto > total_pendiente:
            raise HTTPException(
                status_code=400, 
                detail=f"El pago excede el saldo pendiente total ({total_pendiente})"
            )

        # 4. Iniciar distribución inteligente
        monto_restante = monto
        
        for cuota in cuotas_pendientes:
            if monto_restante <= 0:
                break
                
            balance_cuota = Decimal(str(cuota.monto_esperado)) - Decimal(str(cuota.monto_abonado))
            
            if monto_restante >= balance_cuota:
                # Paga la cuota completa
                cuota.monto_abonado = Decimal(str(cuota.monto_abonado)) + balance_cuota
                cuota.estado = "pagada"
                monto_restante -= balance_cuota
            else:
                # Pago parcial de la cuota
                cuota.monto_abonado = Decimal(str(cuota.monto_abonado)) + monto_restante
                # Podrías actualizar a "parcial" si tu modelo lo soporta
                monto_restante = Decimal('0')

        # 4.5. Actualizar estado del préstamo si se pagó en su totalidad
        if monto == total_pendiente:
            prestamo.estado = "pagado"

        # 5. Crear el registro del pago
        nuevo_pago = Pago(
            prestamo_id=prestamo.id,
            monto=monto,
            comentario=comentario
        )
        db.add(nuevo_pago)
        db.flush()

        # 6. Registrar en auditoría
        audit = HistoriaOperacion(
            usuario_id=user.id,
            accion="PAGO",
            monto=monto,
            entidad_id=nuevo_pago.id,
            detalles=f"Pago de {monto} registrado para préstamo {prestamo_id}"
        )
        db.add(audit)

        db.commit()
        db.refresh(nuevo_pago)
        return nuevo_pago
        
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

def listar_pagos(db: Session):
    return db.query(Pago).all()
