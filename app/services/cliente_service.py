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

def actualizar_cliente(db: Session, cliente_id: int, datos: dict):
    repo = ClienteRepository(db)
    cliente = repo.get_by_id(cliente_id)
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

def eliminar_cliente(db: Session, cliente_id: int):
    repo = ClienteRepository(db)
    return repo.delete(cliente_id)