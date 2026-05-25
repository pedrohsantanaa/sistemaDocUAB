from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database.session import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    cargo = Column(String, default="usuario") # 'admin' ou 'usuario'
    ativo = Column(Boolean, default=True)

    movimentacoes = relationship("Movimentacao", back_populates="usuario")
