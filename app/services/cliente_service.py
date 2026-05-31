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
    
    # Podríamos agregar validaciones de negocio aquí
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

def listar_clientes(db: Session):
    repo = ClienteRepository(db)
    return repo.get_all()

def eliminar_cliente(db: Session, cliente_id: int):
    repo = ClienteRepository(db)
    return repo.delete(cliente_id)