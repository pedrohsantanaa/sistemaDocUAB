from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.processo import Processo
from app.models.movimentacao import Movimentacao

from app.schemas.processo_schema import ProcessoCriar

def criar_processo(db: Session, dados: ProcessoCriar):
    novo_processo = Processo(
        nome_cliente=dados.nome_cliente,
        cpf_cnpj=dados.cpf_cnpj,
        numero_contrato=dados.numero_contrato,
        tipo_processo=dados.tipo_processo,
        setor_responsavel=dados.setor_responsavel,
        status=dados.status.value if dados.status else "Disponível"
    )
    db.add(novo_processo)
    db.commit()
    db.refresh(novo_processo)
    return novo_processo

def consultar_historico_processo(db: Session, id_processo: int):
    processo = db.query(Processo).filter(Processo.id == id_processo).first()
    
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
        
    historico = db.query(Movimentacao).filter(
        Movimentacao.processo_id == id_processo
    ).order_by(Movimentacao.data_retirada.desc()).all()
    
    return {
        "processo": processo,
        "total_movimentacoes": len(historico),
        "historico": historico
    }

def buscar_processos_com_filtros(db: Session, busca: str = None, status: str = None):
    query = db.query(Processo)
    
    if busca:
        query = query.filter(
            (Processo.nome_cliente.ilike(f"%{busca}%")) |
            (Processo.cpf_cnpj.ilike(f"%{busca}%")) |
            (Processo.numero_contrato.ilike(f"%{busca}%"))
        )
        
    if status and status != "Todos":
        query = query.filter(Processo.status == status)
        
    return query.all()
