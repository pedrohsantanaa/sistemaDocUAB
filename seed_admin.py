import os

from app.database.session import SessionLocal, engine, Base
# Importa todos os módulos de modelo para registrar os relacionamentos do ORM
from app.models import (  # noqa: F401
    processo,
    movimentacao,
    usuario,
    log,
    tipo_processo,
    setor,
    status_processo,
)
from app.models.usuario import Usuario
from app.models.status_processo import StatusProcesso
from app.services.auth_service import get_password_hash

STATUS_INICIAIS = ["Disponível", "Em Posse", "Pendente", "Liquidado", "Arquivado"]
ADMIN_EMAIL = "admin@docuab.com"


def seed_status(db):
    for nome in STATUS_INICIAIS:
        exists = db.query(StatusProcesso).filter(StatusProcesso.nome == nome).first()
        if not exists:
            db.add(StatusProcesso(nome=nome))
            print(f"Status criado: {nome}")
    db.commit()


def seed_admin(db):
    admin_exists = db.query(Usuario).filter(Usuario.email == ADMIN_EMAIL).first()
    if admin_exists:
        print("Usuário administrador já existe.")
        return

    senha = os.getenv("ADMIN_SENHA", "admin123")
    admin = Usuario(
        nome="Administrador",
        email=ADMIN_EMAIL,
        senha_hash=get_password_hash(senha),
        cargo="admin",
        ativo=True,
    )
    db.add(admin)
    db.commit()
    print(f"Usuário administrador inicial criado: {ADMIN_EMAIL}")


def main():
    # Garantir que as tabelas existam
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_status(db)
        seed_admin(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
