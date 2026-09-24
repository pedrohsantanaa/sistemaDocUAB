from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from app.schemas.status_processo_schema import StatusProcessoSchema

class ProcessoBase(BaseModel):
    nome_cliente: str
    cpf_cnpj: str
    numero_contrato: str
    tipo_processo: str
    setor_responsavel: Optional[str] = None
    data_entrada: Optional[datetime] = None
    observacao: Optional[str] = None

class ProcessoCriar(ProcessoBase):
    status_id: int

    @validator('nome_cliente', 'cpf_cnpj', 'numero_contrato', 'tipo_processo')
    def campos_obrigatorios(cls, v):
        if not v or not v.strip():
            raise ValueError("Campo obrigatório")
        return v

class ProcessoSchema(ProcessoBase):
    id: int
    status_id: int
    status: StatusProcessoSchema
    data_entrada: datetime

    class Config:
        from_attributes = True
