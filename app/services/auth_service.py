import os
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request, Depends
from app.models.usuario import Usuario
from app.database.session import get_db
from app.models.log import LogAuditoria
from dotenv import load_dotenv

from app.schemas.usuario_schema import UsuarioCriar

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24)) # 24 horas para facilitar

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificar_senha(senha_plana: str, senha_hasheada: str) -> bool:
    return pwd_context.verify(senha_plana, senha_hasheada)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def criar_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def criar_usuario(db: Session, usuario: UsuarioCriar):
    db_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=get_password_hash(usuario.senha),
        cargo=usuario.cargo,
        ativo=usuario.ativo
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def autenticar_usuario(db: Session, email: str, senha_plana: str):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if not usuario:
        return False
        
    if not verificar_senha(senha_plana, usuario.senha_hash):
        return False
        
    if not usuario.ativo:
        raise HTTPException(status_code=403, detail="Usuário inativo")
        
    return usuario

def get_current_user(request: Request, db: Session = Depends(get_db)):
    # Tentar obter do Header Authorization (Padrão SPA)
    auth_header = request.headers.get("Authorization")
    token = None
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    
    # Se não houver no header, tentar no cookie (Legado/Jinja2)
    if not token:
        token_cookie = request.cookies.get("access_token")
        if token_cookie:
            if token_cookie.startswith("Bearer "):
                token = token_cookie[7:]
            else:
                token = token_cookie

    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
        
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    return usuario

def is_admin(usuario: Usuario):
    if not usuario or usuario.cargo != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Somente administradores"
        )
    return True

def registrar_log_auditoria(db: Session, usuario_id: int, acao: str, recurso: str, detalhes: str):
    novo_log = LogAuditoria(
        usuario_id = usuario_id,
        acao_realizada = acao,
        recurso_afetado = recurso,
        detalhes = detalhes
    )
    db.add(novo_log)
    db.commit()
