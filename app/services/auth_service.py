import os
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.usuario import Usuario
from app.models.log import LogAuditoria
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificar_senha(senha_plana: str, senha_hasheada: str) -> bool:
    return pwd_context.verify(senha_plana, senha_hasheada)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def autenticar_usuario(db: Session, email: str, senha_plana: str):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if not usuario:
        return False
        
    if not verificar_senha(senha_plana, usuario.senha_hash):
        return False
        
    if not usuario.ativo:
        raise HTTPException(status_code=403, detail="Usuário inativo")
        
    return usuario

def registrar_log_auditoria(db: Session, usuario_id: int, acao: str, recurso: str, detalhes: str):
    novo_log = LogAuditoria(
        usuario_id = usuario_id,
        acao_realizada = acao,
        recurso_afetado = recurso,
        detalhes = detalhes
    )
    db.add(novo_log)
    db.commit()
