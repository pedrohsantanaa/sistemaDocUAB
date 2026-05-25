from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.processo import Processo
from app.models.movimentacao import Movimentacao
from app.schemas.movimentacao_schema import MovimentacaoCriar, MovimentacaoDevolucao
from datetime import datetime

def registrar_retirada(db: Session, dados: MovimentacaoCriar):
    processo = db.query(Processo).filter(Processo.id == dados.processo_id).first()
    
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
        
    if processo.status != "Disponível":
        raise HTTPException(status_code=400, detail="Processo indisponível para retirada")
        
    nova_movimentacao = Movimentacao(
        processo_id = dados.processo_id,
        usuario_id = dados.usuario_id,
        setor_destino = dados.setor_destino,
        observacoes = dados.observacoes
    )
    
    processo.status = "Em Posse"
    
    db.add(nova_movimentacao)
    db.commit()
    db.refresh(nova_movimentacao)
    
    return nova_movimentacao

def registrar_devolucao(db: Session, dados: MovimentacaoDevolucao):
    mov = db.query(Movimentacao).filter(
        Movimentacao.id == dados.movimentacao_id, 
        Movimentacao.data_devolucao == None
    ).first()
    
    if not mov:
        raise HTTPException(status_code=404, detail="Movimentação ativa não encontrada")
        
    processo = db.query(Processo).filter(Processo.id == mov.processo_id).first()
    
    mov.data_devolucao = datetime.now()
    processo.status = dados.novo_status_processo.value
    
    db.commit()
    db.refresh(mov)
    
    return mov
