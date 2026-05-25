from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services import auth_service
from app.schemas.usuario_schema import UsuarioCriar
from app.models.usuario import Usuario
import logging

router = APIRouter(prefix="/usuarios", tags=["Usuários"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def listar_usuarios(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
    
    auth_service.is_admin(current_user)
    
    usuarios = db.query(Usuario).all()
    return templates.TemplateResponse(
        request=request,
        name="usuarios/listar.html", 
        context={"usuarios": usuarios, "usuario_logado": current_user}
    )

@router.get("/cadastrar")
async def form_cadastrar_usuario(
    request: Request,
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
    
    auth_service.is_admin(current_user)
    
    return templates.TemplateResponse(
        request=request,
        name="usuarios/cadastrar.html", 
        context={"usuario_logado": current_user}
    )

@router.post("/cadastrar")
async def cadastrar_usuario(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    cargo: str = Form("usuario"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
    
    auth_service.is_admin(current_user)
    
    try:
        dados = UsuarioCriar(
            nome=nome,
            email=email,
            senha=senha,
            cargo=cargo
        )
        auth_service.criar_usuario(db, dados)
        return RedirectResponse(url="/usuarios?msg=Usuário criado com sucesso", status_code=303)
    except Exception as e:
        logging.error(f"Erro ao cadastrar usuário: {e}")
        return templates.TemplateResponse(
            request=request,
            name="usuarios/cadastrar.html", 
            context={"erro": str(e), "usuario_logado": current_user}
        )
