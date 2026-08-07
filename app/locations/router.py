from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, get_admin_user
from app.models.usuario import Usuario
from . import schemas, services, models
from typing import List

router = APIRouter(prefix="/locations", tags=["locations"])

@router.post("/update", response_model=schemas.Location)
async def update_location(
    location: schemas.LocationCreate,
    db: Session = Depends(get_db),
    current_user: models.Location = Depends(get_current_user)
):
    # Guardar en BD
    new_loc = services.create_location(db, location, user_id=current_user.id)
    
    # Notificar vía WebSocket si hay alguien escuchando
    await services.manager.broadcast_user_location(
        current_user.id, 
        {"latitude": new_loc.latitude, "longitude": new_loc.longitude, "user_id": current_user.id}
    )
    
    return new_loc

@router.websocket("/ws/{user_id}")
async def location_websocket(websocket: WebSocket, user_id: int):
    await services.manager.connect(user_id, websocket)
    try:
        while True:
            # Mantener la conexión abierta
            data = await websocket.receive_text()
            # Podríamos procesar comandos desde el cliente aquí si fuera necesario
    except WebSocketDisconnect:
        services.manager.disconnect(user_id, websocket)

@router.get("/latest", response_model=List[schemas.LatestLocation])
def latest_locations(db: Session = Depends(get_db), admin: Usuario = Depends(get_admin_user)):
    """Última ubicación registrada de cada usuario (Acceso Admin)"""
    rows = services.get_latest_locations(db)
    usuarios = {u.id: u for u in db.query(Usuario).all()}
    result = []
    for loc in rows:
        user = usuarios.get(loc.user_id)
        if not user:
            continue
        result.append(schemas.LatestLocation(
            user_id=user.id,
            username=user.username,
            email=user.email,
            rol=user.rol,
            activo=user.activo,
            estado_cuenta=user.estado_cuenta,
            latitude=loc.latitude,
            longitude=loc.longitude,
            accuracy=loc.accuracy,
            timestamp=loc.timestamp,
        ))
    return result
