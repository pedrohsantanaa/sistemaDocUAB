from sqlalchemy.orm import Session
from app.models.tipo_processo import TipoProcesso
from app.models.setor import Setor
from app.schemas.tipo_processo_schema import TipoProcessoCriar
from app.schemas.setor_schema import SetorCriar
from fastapi import HTTPException

# Tipos de Processo
def get_tipos_processo(db: Session):
    return db.query(TipoProcesso).order_by(TipoProcesso.nome).all()

def criar_tipo_processo(db: Session, tipo: TipoProcessoCriar):
    db_tipo = db.query(TipoProcesso).filter(TipoProcesso.nome == tipo.nome).first()
    if db_tipo:
        raise HTTPException(status_code=400, detail="Tipo de processo já cadastrado")
    
    novo_tipo = TipoProcesso(nome=tipo.nome)
    db.add(novo_tipo)
    db.commit()
    db.refresh(novo_tipo)
    return novo_tipo

def atualizar_tipo_processo(db: Session, tipo_id: int, tipo: TipoProcessoCriar):
    db_tipo = db.query(TipoProcesso).filter(TipoProcesso.id == tipo_id).first()
    if not db_tipo:
        raise HTTPException(status_code=404, detail="Tipo de processo não encontrado")
    
    db_tipo.nome = tipo.nome
    db.commit()
    db.refresh(db_tipo)
    return db_tipo

def deletar_tipo_processo(db: Session, tipo_id: int):
    db_tipo = db.query(TipoProcesso).filter(TipoProcesso.id == tipo_id).first()
    if not db_tipo:
        raise HTTPException(status_code=404, detail="Tipo de processo não encontrado")
    
    db.delete(db_tipo)
    db.commit()
    return True

# Setores
def get_setores(db: Session):
    return db.query(Setor).order_by(Setor.nome).all()

def criar_setor(db: Session, setor: SetorCriar):
    db_setor = db.query(Setor).filter(Setor.nome == setor.nome).first()
    if db_setor:
        raise HTTPException(status_code=400, detail="Setor já cadastrado")
    
    novo_setor = Setor(nome=setor.nome)
    db.add(novo_setor)
    db.commit()
    db.refresh(novo_setor)
    return novo_setor

def atualizar_setor(db: Session, setor_id: int, setor: SetorCriar):
    db_setor = db.query(Setor).filter(Setor.id == setor_id).first()
    if not db_setor:
        raise HTTPException(status_code=404, detail="Setor não encontrado")
    
    db_setor.nome = setor.nome
    db.commit()
    db.refresh(db_setor)
    return db_setor

def deletar_setor(db: Session, setor_id: int):
    db_setor = db.query(Setor).filter(Setor.id == setor_id).first()
    if not db_setor:
        raise HTTPException(status_code=404, detail="Setor não encontrado")
    
    db.delete(db_setor)
    db.commit()
    return True
