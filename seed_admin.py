from app.database.session import SessionLocal, engine, Base
from app.models import Usuario, StatusProcesso, Processo, Movimentacao, LogAuditoria, Setor, TipoProcesso
from app.services.auth_service import get_password_hash

def seed_status(db):
    status_iniciais = ["Disponível", "Em Posse", "Pendente", "Liquidado", "Arquivado"]
    for nome in status_iniciais:
        exists = db.query(StatusProcesso).filter(StatusProcesso.nome == nome).first()
        if not exists:
            novo_status = StatusProcesso(nome=nome)
            db.add(novo_status)
            print(f"Status criado: {nome}")
        db.commit()

        def seed_admin():
            # Garantir que as tabelas existam
            Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Criar status iniciais primeiro
        seed_status(db)

        admin_exists = db.query(Usuario).filter(Usuario.email == "admin@docuab.com").first()
        if not admin_exists:
            admin = Usuario(
                nome="Administrador",
                email="admin@docuab.com",
                senha_hash=get_password_hash("admin123"),
                cargo="admin",
                ativo=True
            )
            db.add(admin)
            db.commit()
            print("Usuário administrador inicial criado: admin@docuab.com / admin123")
        else:
            print("Usuário administrador já existe.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()