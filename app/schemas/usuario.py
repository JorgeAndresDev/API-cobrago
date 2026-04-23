from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UsuarioOut(BaseModel):
    id: int
    username: str
    email: str
    activo: bool

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    correo: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None