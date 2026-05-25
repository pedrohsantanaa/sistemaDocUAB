from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    cargo: str = "usuario"
    ativo: bool = True

class UsuarioCriar(UsuarioBase):
    senha: str

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class Usuario(UsuarioBase):
    id: int

    class Config:
        from_attributes = True
