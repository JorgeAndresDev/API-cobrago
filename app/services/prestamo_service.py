from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models import Prestamo, Cuota, Cliente, HistoriaOperacion
from app.repositories.prestamo_repository import PrestamoRepository
from decimal import Decimal

def generar_cuotas(prestamo: Prestamo):
    cuotas = []
    # Usar monto_total (con intereses) o el monto base como fallback
    valor_total = Decimal(str(prestamo.monto_total or prestamo.monto))
    monto_por_cuota = (valor_total / prestamo.num_cuotas).quantize(Decimal('0.01'))
    fecha_base = date.today()

    for i in range(1, prestamo.num_cuotas + 1):
        if prestamo.frecuencia_pago == "diaria":
            fecha = fecha_base + timedelta(days=i)
        elif prestamo.frecuencia_pago == "semanal":
            fecha = fecha_base + timedelta(days=7 * i)
        elif prestamo.frecuencia_pago == "quincenal":
            fecha = fecha_base + timedelta(days=15 * i)
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

from datetime import datetime, timezone
from app.models.usuario import Usuario

def crear_prestamo(db: Session, data, user: Usuario):
    # 1️⃣ VALIDACIÓN DE VENCIMIENTO
    if user.fecha_vencimiento and user.fecha_vencimiento.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise ValueError("Su suscripción ha vencido. Por favor, renueve su plan para continuar.")

    # Usamos transacciones atómicas para asegurar consistencia
    if hasattr(data, "model_dump"): # Compatibilidad Pydantic V2
        prestamo_data = data.model_dump()
    elif hasattr(data, "dict"): # Compatibilidad Pydantic V1
        prestamo_data = data.dict()
    else:
        prestamo_data = data

    # 🔹 RESOLUCIÓN DE CLIENTE CORE:
    client_id_raw = prestamo_data.get("cliente_id")
    if client_id_raw:
        # Intentamos buscar por ID numérico primero
        cliente = None
        try:
            client_id_int = int(client_id_raw)
            cliente = db.query(Cliente).filter(Cliente.id == client_id_int).first()
        except (ValueError, TypeError):
            pass
        
        # Si no se encontró por ID, buscamos por cédula
        if not cliente:
            cliente = db.query(Cliente).filter(Cliente.cedula == str(client_id_raw)).first()
        
        if not cliente:
            raise ValueError(f"Cliente con identificador {client_id_raw} no encontrado.")

        # 2️⃣ VALIDACIÓN DE PROPIEDAD
        if user.rol != "admin" and cliente.usuario_id != user.id:
            raise ValueError("No tiene permisos para crear un préstamo a un cliente ajeno.")
        
        # Sobreescribimos con el ID numérico real para la DB
        prestamo_data["cliente_id"] = cliente.id

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
            usuario_id=user.id,
            accion="CREAR_PRESTAMO",
            monto=prestamo.monto_total or prestamo.monto,
            entidad_id=prestamo.id,
            detalles=f"Préstamo de {prestamo.monto} (Total: {prestamo.monto_total}) creado para cliente {prestamo.cliente_id}"
        )
        db.add(audit)

        db.commit()
        db.refresh(prestamo)
        return prestamo
    except Exception as e:
        db.rollback()
        raise e

def listar_prestamos(db: Session, user: Usuario):
    query = db.query(Prestamo)
    
    # FILTRADO DE PRIVACIDAD
    if user.rol != "admin":
        # Unimos con Cliente para filtrar por el dueño del cliente
        query = query.join(Cliente).filter(Cliente.usuario_id == user.id)
    
    prestamos = query.all()
    # Mapeamos para incluir el nombre del cliente
    for p in prestamos:
        p.nombre_cliente = p.cliente.nombre if p.cliente else "Desconocido"
    return prestamos

def eliminar_prestamo(db: Session, prestamo_id: int, user: Usuario):
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if not prestamo:
        return None
        
    # VALIDACIÓN DE PROPIEDAD
    if user.rol != "admin" and prestamo.cliente.usuario_id != user.id:
        raise ValueError("No tiene permisos para eliminar este préstamo.")

    repo = PrestamoRepository(db)
    return repo.delete(prestamo_id)