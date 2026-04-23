from app.repositories.base import BaseRepository
from app.models.prestamo import Prestamo
from sqlalchemy.orm import Session

class PrestamoRepository(BaseRepository[Prestamo]):
    def __init__(self, db: Session):
        super().__init__(Prestamo, db)

    def get_by_cliente(self, cliente_id: int):
        return self.db.query(Prestamo).filter(Prestamo.cliente_id == cliente_id).all()
