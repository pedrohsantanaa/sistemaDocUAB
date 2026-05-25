from pydantic import BaseModel, validator
from typing import Optional

class TipoProcessoBase(BaseModel):
    nome: str

    @validator('nome')
    def nome_nao_vazio(cls, v):
        if not v or not v.strip():
            raise ValueError("Nome é obrigatório")
        return v.strip()

class TipoProcessoCriar(TipoProcessoBase):
    pass

class TipoProcessoSchema(TipoProcessoBase):
    id: int

    class Config:
        orm_mode = True
