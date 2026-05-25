from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.processo import Processo
from app.models.movimentacao import Movimentacao
from app.models.status_processo import StatusProcesso
from app.schemas.movimentacao_schema import MovimentacaoCriar, MovimentacaoDevolucao
from datetime import datetime

def registrar_retirada(db: Session, dados: MovimentacaoCriar):
    processo = db.query(Processo).filter(Processo.id == dados.processo_id).first()
    
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    # Busca o status "Disponível" para verificar se pode retirar
    # Se o nome mudar, o sistema precisaria de uma configuração de qual status representa "disponível"
    # Por enquanto, mantemos a lógica por nome.
    status_disponivel = db.query(StatusProcesso).filter(StatusProcesso.nome == "Disponível").first()
    if not status_disponivel or processo.status_id != status_disponivel.id:
        raise HTTPException(status_code=400, detail="Processo indisponível para retirada")
        
    nova_movimentacao = Movimentacao(
        processo_id = dados.processo_id,
        usuario_id = dados.usuario_id,
        setor_destino = dados.setor_destino,
        observacoes = dados.observacoes
    )
    
    status_em_posse = db.query(StatusProcesso).filter(StatusProcesso.nome == "Em Posse").first()
    if not status_em_posse:
        # Se não existir, talvez devêssemos criar ou dar erro? 
        # Idealmente o seed garante isso.
        raise HTTPException(status_code=500, detail="Status 'Em Posse' não configurado no sistema")
        
    processo.status_id = status_em_posse.id
    
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
    
    # novo_status_processo agora deve vir como ID ou nome dependendo do schema
    # Vamos assumir que o schema enviará o nome ou ID. 
    # Atualmente o schema MovimentacaoDevolucao usa um Enum.
    
    nome_status = dados.novo_status_processo
    if hasattr(nome_status, 'value'):
        nome_status = nome_status.value
        
    status_obj = db.query(StatusProcesso).filter(StatusProcesso.nome == nome_status).first()
    if not status_obj:
        # Se for um ID em formato de string
        if str(nome_status).isdigit():
             status_obj = db.query(StatusProcesso).filter(StatusProcesso.id == int(nome_status)).first()
        
    if not status_obj:
        raise HTTPException(status_code=400, detail=f"Status '{nome_status}' não encontrado")
        
    processo.status_id = status_obj.id
    
    db.commit()
    db.refresh(mov)
    
    return mov
