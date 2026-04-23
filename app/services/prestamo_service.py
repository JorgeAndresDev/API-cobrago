from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models import Prestamo, Cuota, Cliente, HistoriaOperacion
from app.repositories.prestamo_repository import PrestamoRepository
from decimal import Decimal

def generar_cuotas(prestamo: Prestamo):
    cuotas = []
    monto_total = Decimal(str(prestamo.monto))
    monto_por_cuota = (monto_total / prestamo.num_cuotas).quantize(Decimal('0.01'))
    fecha_base = date.today()

    for i in range(1, prestamo.num_cuotas + 1):
        if prestamo.frecuencia_pago == "diaria":
            fecha = fecha_base + timedelta(days=i)
        elif prestamo.frecuencia_pago == "semanal":
            fecha = fecha_base + timedelta(days=7 * i)
        elif prestamo.frecuencia_pago == "mensual":
            fecha = fecha_base + timedelta(days=30 * i)
        else:
            raise ValueError("Frecuencia inválida")

        cuota = Cuota(
            numero_cuota=i,
            fecha_vencimiento=fecha,
            monto_esperado=monto_por_cuota,
            monto_abonado=Decimal('0.00'),
            estado="pendiente"
        )
        cuotas.append(cuota)

    return cuotas

def crear_prestamo(db: Session, data, usuario_id: int):
    # Usamos transacciones atómicas para asegurar consistencia
    if hasattr(data, "model_dump"): # Compatibilidad Pydantic V2
        prestamo_data = data.model_dump()
    elif hasattr(data, "dict"): # Compatibilidad Pydantic V1
        prestamo_data = data.dict()
    else:
        prestamo_data = data

    try:
        # 1. Crear el préstamo
        prestamo = Prestamo(**prestamo_data)
        db.add(prestamo)
        db.flush() # Obtener ID sin commitear aún

        # 2. Generar cuotas
        cuotas = generar_cuotas(prestamo)
        for cuota in cuotas:
            cuota.prestamo_id = prestamo.id
            db.add(cuota)

        # 3. Registrar en auditoría
        audit = HistoriaOperacion(
            usuario_id=usuario_id,
            accion="CREAR_PRESTAMO",
            monto=prestamo.monto,
            entidad_id=prestamo.id,
            detalles=f"Préstamo de {prestamo.monto} creado para cliente {prestamo.cliente_id}"
        )
        db.add(audit)

        db.commit()
        db.refresh(prestamo)
        return prestamo
    except Exception as e:
        db.rollback()
        raise e

def listar_prestamos(db: Session):
    prestamos = db.query(Prestamo).all()
    # Mapeamos para incluir el nombre del cliente y el saldo
    for p in prestamos:
        p.nombre_cliente = p.cliente.nombre if p.cliente else "Desconocido"
        saldo_pendiente = sum((c.monto_esperado or Decimal('0.00')) - (c.monto_abonado or Decimal('0.00')) for c in p.cuotas)
        p.saldo = saldo_pendiente
    return prestamos

def eliminar_prestamo(db: Session, prestamo_id: int):
    repo = PrestamoRepository(db)
    return repo.delete(prestamo_id)