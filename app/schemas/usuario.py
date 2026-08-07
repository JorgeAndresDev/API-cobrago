from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UsuarioCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UsuarioOut(BaseModel):
    id: int
    username: str
    email: str
    activo: bool
    rol: str
    estado_cuenta: str
    plan_suscripcion: str
    fecha_vencimiento: Optional[datetime] = None

    class Config:
        from_attributes = True

class UsuarioAdminUpdate(BaseModel):
    activo: bool | None = None
    rol: str | None = None
    estado_cuenta: str | None = None
    plan_suscripcion: str | None = None
    fecha_vencimiento: Optional[datetime] = None

class LoginRequest(BaseModel):
    correo: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str