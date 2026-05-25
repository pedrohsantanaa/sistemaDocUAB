from pydantic import BaseModel, validator
from typing import Optional
from enum import Enum

class StatusEnum(str, Enum):
    disponivel = "Disponível"
    liquidado = "Liquidado"
    arquivado = "Arquivado"

class MovimentacaoCriar(BaseModel):
    processo_id: int
    usuario_id: int
    setor_destino: str
    observacoes: Optional[str] = None

    @validator('setor_destino')
    def setor_destino_nao_vazio(cls, v):
        if not v or not v.strip():
            raise ValueError("Setor de destino é obrigatório")
        return v

class MovimentacaoDevolucao(BaseModel):
    movimentacao_id: int
    novo_status_processo: StatusEnum
