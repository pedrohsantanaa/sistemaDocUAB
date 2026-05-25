"""
Módulo de Serviço de Processos
Responsável pela lógica de negócio relacionada à gestão de processos físicos.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.processo import Processo
from app.models.movimentacao import Movimentacao
from app.schemas.processo_schema import ProcessoCriar

def criar_processo(db: Session, dados: ProcessoCriar):
    """
    Cria um novo registro de processo no banco de dados.
    Utiliza o esquema ProcessoCriar para validar os dados de entrada.
    """
    novo_processo = Processo(
        nome_cliente=dados.nome_cliente,
        cpf_cnpj=dados.cpf_cnpj,
        numero_contrato=dados.numero_contrato,
        tipo_processo=dados.tipo_processo,
        setor_responsavel=dados.setor_responsavel,
        status_id=dados.status_id,
        data_entrada=dados.data_entrada,
        observacao=dados.observacao
    )
    
    try:
        db.add(novo_processo)
        db.commit()
        db.refresh(novo_processo)
        return novo_processo
    except Exception as e:
        db.rollback()
        # Em produção, registraríamos o erro real em um log (logger.error(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Não foi possível cadastrar o processo no momento."
        )

def consultar_historico_processo(db: Session, id_processo: int):
    """
    Retorna os detalhes de um processo e sua lista completa de movimentações.
    """
    processo = db.query(Processo).filter(Processo.id == id_processo).first()
    
    if not processo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Processo não localizado no sistema."
        )
        
    # Busca as movimentações ordenadas da mais recente para a mais antiga
    historico = db.query(Movimentacao).filter(
        Movimentacao.processo_id == id_processo
    ).order_by(Movimentacao.data_retirada.desc()).all()
    
    return {
        "processo": processo,
        "total_movimentacoes": len(historico),
        "historico": historico
    }

def buscar_processos_com_filtros(db: Session, busca: str = None, status: str = None):
    """
    Realiza busca filtrada de processos por texto (cliente, contrato, cpf) ou por status.
    """
    query = db.query(Processo)
    
    if busca:
        # Aplica filtro OR em múltiplos campos para facilitar a busca do usuário
        query = query.filter(
            (Processo.nome_cliente.ilike(f"%{busca}%")) |
            (Processo.cpf_cnpj.ilike(f"%{busca}%")) |
            (Processo.numero_contrato.ilike(f"%{busca}%"))
        )
        
    if status and status != "Todos":
        # Se status for numérico (ID), filtra por status_id, senão tenta pelo nome (legado ou texto)
        if status.isdigit():
            query = query.filter(Processo.status_id == int(status))
        else:
            from app.models.status_processo import StatusProcesso
            query = query.join(StatusProcesso).filter(StatusProcesso.nome == status)
        
    return query.all()
