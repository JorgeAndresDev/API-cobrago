from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from typing import List, Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)

    async def broadcast_user_location(self, user_id: int, location: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(location)

manager = ConnectionManager()

def create_location(db: Session, location: schemas.LocationCreate, user_id: int):
    db_location = models.Location(**location.model_dump(), user_id=user_id)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def get_latest_location(db: Session, user_id: int):
    return db.query(models.Location).filter(models.Location.user_id == user_id).order_by(models.Location.timestamp.desc()).first()

def get_latest_locations(db: Session):
    """Última ubicación registrada de cada usuario con una o más actualizaciones."""
    subq = (
        db.query(
            models.Location.user_id,
            func.max(models.Location.timestamp).label("max_ts"),
        )
        .group_by(models.Location.user_id)
        .subquery()
    )
    return (
        db.query(models.Location)
        .join(subq, (models.Location.user_id == subq.c.user_id) & (models.Location.timestamp == subq.c.max_ts))
        .all()
    )
