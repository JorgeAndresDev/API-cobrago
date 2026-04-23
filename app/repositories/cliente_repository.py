from app.repositories.base import BaseRepository
from app.models.cliente import Cliente
from sqlalchemy.orm import Session

class ClienteRepository(BaseRepository[Cliente]):
    def __init__(self, db: Session):
        super().__init__(Cliente, db)

    def get_by_cedula(self, cedula: str) -> Cliente:
        return self.db.query(Cliente).filter(Cliente.cedula == cedula).first()
