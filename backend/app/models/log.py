from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.session import Base

class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    acao_realizada = Column(String, nullable=False)
    recurso_afetado = Column(String, nullable=False)
    detalhes = Column(String, nullable=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
