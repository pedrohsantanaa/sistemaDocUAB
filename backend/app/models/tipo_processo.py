from sqlalchemy import Column, Integer, String
from app.database.session import Base

class TipoProcesso(Base):
    __tablename__ = "tipos_processo"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, nullable=False, index=True)
