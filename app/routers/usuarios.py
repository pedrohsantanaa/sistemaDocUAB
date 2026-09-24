from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.services import auth_service
from app.schemas.usuario_schema import UsuarioCriar, UsuarioEditar, Usuario as UsuarioSchema
from app.models.usuario import Usuario
import logging

router = APIRouter(prefix="/api/usuarios", tags=["Usuários"])

@router.get("/", response_model=List[UsuarioSchema])
async def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.require_admin)
):
    usuarios = db.query(Usuario).all()
    return usuarios

@router.post("/cadastrar", response_model=UsuarioSchema, status_code=status.HTTP_201_CREATED)
async def cadastrar_usuario(
    dados: UsuarioCriar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.require_admin)
):
    try:
        novo_usuario = auth_service.criar_usuario(db, dados)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "criar_usuario", f"usuario:{novo_usuario.id}",
            f"Usuário '{novo_usuario.email}' criado"
        )
        return novo_usuario
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao cadastrar usuário")
        raise HTTPException(status_code=400, detail="Não foi possível cadastrar o usuário.")

@router.put("/{usuario_id}", response_model=UsuarioSchema)
async def editar_usuario(
    usuario_id: int,
    dados: UsuarioEditar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.require_admin)
):
    try:
        usuario_atualizado = auth_service.atualizar_usuario(db, usuario_id, dados)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "editar_usuario", f"usuario:{usuario_id}",
            f"Usuário '{usuario_atualizado.email}' atualizado"
        )
        return usuario_atualizado
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao editar usuário %s", usuario_id)
        raise HTTPException(status_code=400, detail="Não foi possível editar o usuário.")
