from sqlalchemy import Column, Integer, String
from app.database.session import Base

class StatusProcesso(Base):
    __tablename__ = "status_processos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, nullable=False, index=True)
