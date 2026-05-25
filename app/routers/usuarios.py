from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.services import auth_service
from app.schemas.usuario_schema import UsuarioCriar, Usuario as UsuarioSchema
from app.models.usuario import Usuario
import logging

router = APIRouter(prefix="/api/usuarios", tags=["Usuários"])

@router.get("/", response_model=List[UsuarioSchema])
async def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    auth_service.is_admin(current_user)
    usuarios = db.query(Usuario).all()
    return usuarios

@router.post("/cadastrar", response_model=UsuarioSchema, status_code=status.HTTP_201_CREATED)
async def cadastrar_usuario(
    dados: UsuarioCriar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    auth_service.is_admin(current_user)
    try:
        novo_usuario = auth_service.criar_usuario(db, dados)
        return novo_usuario
    except Exception as e:
        logging.error(f"Erro ao cadastrar usuário: {e}")
        raise HTTPException(status_code=400, detail=str(e))
