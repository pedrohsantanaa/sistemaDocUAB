from pydantic import BaseModel, validator
from typing import Optional
from enum import Enum

class ProcessoStatus(str, Enum):
    disponivel = "Disponível"
    em_posse = "Em Posse"
    pendente = "Pendente"
    liquidado = "Liquidado"
    arquivado = "Arquivado"

class ProcessoCriar(BaseModel):
    nome_cliente: str
    cpf_cnpj: str
    numero_contrato: str
    tipo_processo: str
    setor_responsavel: str
    status: Optional[ProcessoStatus] = ProcessoStatus.disponivel

    @validator('nome_cliente', 'cpf_cnpj', 'numero_contrato', 'tipo_processo', 'setor_responsavel')
    def campos_obrigatorios(cls, v):
        if not v or not v.strip():
            raise ValueError("Campo obrigatório")
        return v
