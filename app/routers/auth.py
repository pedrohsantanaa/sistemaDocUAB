from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services import auth_service
import logging

router = APIRouter(tags=["Autenticação"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = auth_service.autenticar_usuario(db, email, senha)
    if not usuario:
        return templates.TemplateResponse(
            request=request, 
            name="login.html", 
            context={"erro": "E-mail ou senha incorretos"}
        )
    
    access_token = auth_service.criar_access_token(data={"sub": usuario.email})
    
    # Armazenar token em cookie para facilitar o uso em templates
    response = RedirectResponse(url="/processos", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response
