from sqlalchemy.orm import Session
from app.models.cliente import Cliente
from app.repositories.cliente_repository import ClienteRepository

def crear_cliente(
    db: Session,
    nombre: str,
    cedula: str,
    telefono: str = None,
    direccion: str = None,
    latitud: float = None,
    longitud: float = None,
    observaciones: str = None,
    nivel_riesgo: str = "Bajo",
    foto_url: str = None,
    foto_local_path: str = None,
    usuario_id: int = None,
):
    repo = ClienteRepository(db)
    
    # 🔹 Validación: Evitar duplicados por cédula
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
        usuario_id=usuario_id
    )
    return repo.create(cliente)

def actualizar_cliente(db: Session, cliente_id: str, datos: dict):
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

def listar_clientes(db: Session):
    repo = ClienteRepository(db)
    return repo.get_all()

def eliminar_cliente(db: Session, cliente_id: str):
    repo = ClienteRepository(db)
    # Intentar buscar por ID interno
    cliente = None
    try:
        # Si es un número, buscamos por ID primario
        client_id_int = int(cliente_id)
        cliente = repo.get_by_id(client_id_int)
    except (ValueError, TypeError):
        pass
    
    # Si no se encontró o no era un ID válido, buscamos por cédula
    if not cliente:
        cliente = db.query(Cliente).filter(Cliente.cedula == str(cliente_id)).first()
    
    if cliente:
        return repo.delete(cliente.id)
    return None