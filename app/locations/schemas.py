from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LocationBase(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
    timestamp: Optional[datetime] = None

class LatestLocation(BaseModel):
    user_id: int
    username: str
    email: str
    rol: str
    activo: bool
    estado_cuenta: str
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    timestamp: datetime
