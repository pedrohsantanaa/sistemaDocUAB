import logging
import os
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request, Depends
from app.models.usuario import Usuario
from app.database.session import get_db
from app.models.log import LogAuditoria
from dotenv import load_dotenv

from app.schemas.usuario_schema import UsuarioCriar, UsuarioEditar

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or SECRET_KEY in ("your-secret-key", "TROQUE_POR_UMA_CHAVE_FORTE_ALEATORIA"):
    raise RuntimeError(
        "SECRET_KEY não definida ou inválida nas variáveis de ambiente. "
        "Copie .env.example para .env e gere uma chave: "
        "python -c \"import secrets; print(secrets.token_hex(32))\""
    )
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificar_senha(senha_plana: str, senha_hasheada: str) -> bool:
    return pwd_context.verify(senha_plana, senha_hasheada)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def criar_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def criar_usuario(db: Session, usuario: UsuarioCriar):
    db_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=get_password_hash(usuario.senha),
        cargo=usuario.cargo,
        setor=usuario.setor,
        ativo=usuario.ativo
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def atualizar_usuario(db: Session, usuario_id: int, dados: UsuarioEditar):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if dados.nome is not None:
        db_usuario.nome = dados.nome
    if dados.email is not None:
        db_usuario.email = dados.email
    if dados.cargo is not None:
        db_usuario.cargo = dados.cargo
    if dados.setor is not None:
        db_usuario.setor = dados.setor
    if dados.ativo is not None:
        db_usuario.ativo = dados.ativo
    if dados.senha is not None and dados.senha.strip() != "":
        db_usuario.senha_hash = get_password_hash(dados.senha)
    
    try:
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except Exception as e:
        db.rollback()
        raise e

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
    # Autenticação exclusivamente via header Authorization (Bearer) — SPA
    auth_header = request.headers.get("Authorization")
    token = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado ou inválido"
        )
        
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    return usuario

def is_admin(usuario: Usuario):
    if not usuario or usuario.cargo != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Somente administradores"
        )
    return True

def require_admin(current_user: Usuario = Depends(get_current_user)):
    """Dependency de rota: exige usuário autenticado com cargo 'admin'."""
    is_admin(current_user)
    return current_user

def registrar_log_auditoria(db: Session, usuario_id: int, acao: str, recurso: str, detalhes: str):
    """Registra ação crítica em logs_auditoria. Falha de log não interrompe a operação."""
    try:
        novo_log = LogAuditoria(
            usuario_id=usuario_id,
            acao_realizada=acao,
            recurso_afetado=recurso,
            detalhes=detalhes
        )
        db.add(novo_log)
        db.commit()
    except Exception:
        db.rollback()
        logging.getLogger(__name__).exception(
            "Falha ao registrar log de auditoria (%s/%s)", acao, recurso
        )
