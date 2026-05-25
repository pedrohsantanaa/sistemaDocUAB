from app.database.session import SessionLocal
from app.models.usuario import Usuario
from app.models.movimentacao import Movimentacao # Import necessário para relacionamentos
from app.models.processo import Processo         # Import necessário para relacionamentos
from app.services.auth_service import get_password_hash

def seed_admin():
    db = SessionLocal()
    try:
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
