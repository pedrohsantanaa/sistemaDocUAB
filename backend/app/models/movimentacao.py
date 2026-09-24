from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_retirada = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data_devolucao = Column(DateTime(timezone=True), nullable=True)
    setor_destino = Column(String, nullable=False)
    observacoes = Column(String, nullable=True)

    processo = relationship("Processo", back_populates="movimentacoes")
    usuario = relationship("Usuario", back_populates="movimentacoes")
