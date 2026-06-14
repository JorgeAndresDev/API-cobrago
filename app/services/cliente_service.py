from sqlalchemy.orm import Session
from app.models.cliente import Cliente
from app.repositories.cliente_repository import ClienteRepository
from datetime import datetime, timezone
from app.config.plans import get_plan_config
from app.models.usuario import Usuario

def crear_cliente(
    db: Session,
    nombre: str,
    cedula: str,
    user: Usuario, # Ahora recibimos el usuario completo para validar plan
    telefono: str = None,
    direccion: str = None,
    latitud: float = None,
    longitud: float = None,
    observaciones: str = None,
    nivel_riesgo: str = "Bajo",
    foto_url: str = None,
    foto_local_path: str = None,
):
    repo = ClienteRepository(db)
    
    # 1️⃣ VALIDACIÓN DE PLAN Y VENCIMIENTO
    plan_config = get_plan_config(user.plan_suscripcion)
    
    # Verificar Vencimiento
    if user.fecha_vencimiento and user.fecha_vencimiento.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise ValueError("Su suscripción ha vencido. Por favor, renueve su plan para continuar.")

    # Verificar Límite de Clientes
    clientes_actuales = db.query(Cliente).filter(Cliente.usuario_id == user.id).count()
    if clientes_actuales >= plan_config["max_clientes"]:
        raise ValueError(f"Ha alcanzado el límite de {plan_config['max_clientes']} clientes para su {plan_config['nombre']}.")

    # 🔹 Validación: Evitar duplicados por cédula (dentro de su propia cartera)
    # Nota: Permitimos la misma cédula para diferentes cobradores si es necesario, 
    # pero aquí mantenemos la unicidad global por ahora según diseño previo.
    existente = db.query(Cliente).filter(Cliente.cedula == cedula).first()
    if existente:
        raise ValueError(f"La cédula {cedula} ya se encuentra registrada.")

    cliente = Cliente(
        nombre=nombre,
        cedula=cedula,
        telefono=telefono,
        direccion=direccion,
        latitud=latitud,
        longitud=longitud,
        observaciones=observaciones,
        nivel_riesgo=nivel_riesgo,
        foto_url=foto_url,
        foto_local_path=foto_local_path,
        usuario_id=user.id
    )
    return repo.create(cliente)

def actualizar_cliente(db: Session, cliente_id: str, datos: dict, user: Usuario):
    repo = ClienteRepository(db)
    # Intentar buscar por ID interno
    cliente = None
    try:
        client_id_int = int(cliente_id)
        cliente = repo.get_by_id(client_id_int)
    except (ValueError, TypeError):
        pass
    
    # Si no se encontró por ID, buscamos por cédula
    if not cliente:
        cliente = db.query(Cliente).filter(Cliente.cedula == str(cliente_id)).first()
        
    if not cliente:
        return None

    # VALIDACIÓN DE PROPIEDAD
    if user.rol != "admin" and cliente.usuario_id != user.id:
        raise ValueError("No tiene permisos para modificar este cliente.")
    
    # Si se intenta cambiar la cédula, validar que no choque con otra
    if "cedula" in datos and datos["cedula"] != cliente.cedula:
        existente = db.query(Cliente).filter(Cliente.cedula == datos["cedula"]).first()
        if existente:
            raise ValueError(f"La nueva cédula {datos['cedula']} ya pertenece a otro cliente.")

    for key, value in datos.items():
        if value is not None:
            setattr(cliente, key, value)
    
    db.commit()
    db.refresh(cliente)
    return cliente

def listar_clientes(db: Session, user: Usuario):
    query = db.query(Cliente)
    # Si no es admin, solo ve sus propios clientes
    if user.rol != "admin":
        query = query.filter(Cliente.usuario_id == user.id)
    return query.all()

def eliminar_cliente(db: Session, cliente_id: str, user: Usuario):
    repo = ClienteRepository(db)
    # Intentar buscar por ID interno
    cliente = None
    try:
        # Si es un número, buscamos por ID primario
        client_id_int = int(cliente_id)
        cliente = repo.get_by_id(client_id_int)
    except (ValueError, TypeError):
        pass
    
    # Si no se encontró por ID, buscamos por cédula
    if not cliente:
        cliente = db.query(Cliente).filter(Cliente.cedula == str(cliente_id)).first()
    
    if not cliente:
        return None

    # VALIDACIÓN DE PROPIEDAD
    if user.rol != "admin" and cliente.usuario_id != user.id:
        raise ValueError("No tiene permisos para eliminar este cliente.")
    
    if cliente:
        return repo.delete(cliente.id)
    return None