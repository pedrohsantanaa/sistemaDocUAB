from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class Processo(Base):
    __tablename__ = "processos"

    id = Column(Integer, primary_key=True, index=True)
    nome_cliente = Column(String, nullable=False)
    cpf_cnpj = Column(String, nullable=False, unique=True)
    numero_contrato = Column(String, nullable=False, unique=True)
    tipo_processo = Column(String, nullable=False)
    
    status_id = Column(Integer, ForeignKey("status_processos.id"), nullable=False)
    status = relationship("StatusProcesso")
    
    data_entrada = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    setor_responsavel = Column(String, nullable=False)
    observacao = Column(Text, nullable=True)

    movimentacoes = relationship("Movimentacao", back_populates="processo", cascade="all, delete-orphan")
