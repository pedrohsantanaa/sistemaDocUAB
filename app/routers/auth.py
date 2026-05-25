from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services import auth_service
from app.schemas.usuario_schema import LoginRequest, Usuario
import logging

router = APIRouter(tags=["Autenticação"])

@router.post("/login")
async def login(
    dados: LoginRequest,
    db: Session = Depends(get_db)
):
    usuario = auth_service.autenticar_usuario(db, dados.email, dados.senha)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos"
        )
    
    access_token = auth_service.criar_access_token(data={"sub": usuario.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "cargo": usuario.cargo
        }
    }

@router.get("/me", response_model=Usuario)
async def get_me(current_user: Usuario = Depends(auth_service.get_current_user)):
    return current_user

@router.post("/logout")
async def logout():
    return {"message": "Logout realizado com sucesso"}
