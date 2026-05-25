from pydantic import BaseModel

class StatusProcessoBase(BaseModel):
    nome: str

class StatusProcessoCriar(StatusProcessoBase):
    pass

class StatusProcessoSchema(StatusProcessoBase):
    id: int

    class Config:
        from_attributes = True
