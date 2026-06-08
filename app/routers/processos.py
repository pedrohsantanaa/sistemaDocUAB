from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.session import get_db
from app.services import processo_service, auth_service, configuracao_service, movimentacao_service
from app.models.usuario import Usuario
from app.schemas.processo_schema import ProcessoCriar, ProcessoSchema
from app.schemas.movimentacao_schema import MovimentacaoCriar, MovimentacaoDevolucao
import logging

router = APIRouter(prefix="/api/processos", tags=["Processos"])

@router.get("/")
async def listar_processos(
    busca: Optional[str] = None, 
    status: Optional[str] = None, 
    setor: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        processos_encontrados = processo_service.buscar_processos_com_filtros(db, busca, status, setor, current_user)
        
        # Garantir que o status seja carregado para cada processo antes de retornar
        # Isso resolve o problema de serialização lazy do SQLAlchemy
        from app.schemas.processo_schema import ProcessoSchema
        processos_serializados = [ProcessoSchema.from_orm(p) for p in processos_encontrados]

        # Calcular estatísticas básicas filtradas pelo setor do usuário (se não for admin)
        from app.models.processo import Processo
        from app.models.status_processo import StatusProcesso

        query_stats = db.query(Processo)
        if current_user.cargo != "admin":
            query_stats = query_stats.filter(Processo.setor_responsavel == current_user.setor)

        total_processos = query_stats.count()

        def get_count_by_status(nome_status):
            return query_stats.join(StatusProcesso).filter(StatusProcesso.nome == nome_status).count()

        processos_disponiveis = get_count_by_status("Disponível")
        processos_em_posse = get_count_by_status("Em Posse")
        processos_pendentes = get_count_by_status("Pendente")

        return {
            "processos": processos_serializados,
            "stats": {
                "total": total_processos,
                "disponiveis": processos_disponiveis,
                "em_posse": processos_em_posse,

                "pendentes": processos_pendentes
            }
        }

    except Exception as e:
        logging.error(f"Erro ao listar processos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cadastrar", status_code=status.HTTP_201_CREATED)
async def cadastrar_processo(
    dados: ProcessoCriar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        novo_processo = processo_service.criar_processo(db, dados, current_user)
        return ProcessoSchema.from_orm(novo_processo)
    except Exception as e:
        logging.error(f"Erro ao cadastrar processo: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{processo_id}/historico")
async def historico_processo(
    processo_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        dados_historico = processo_service.consultar_historico_processo(db, processo_id)
        return dados_historico
    except Exception as e:
        logging.error(f"Erro ao consultar histórico: {e}")
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/movimentar/retirada")
async def retirar_processo(
    processo_id: int,
    setor_destino: str,
    observacoes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        mov_dados = MovimentacaoCriar(
            processo_id=processo_id,
            usuario_id=current_user.id,
            setor_destino=setor_destino,
            observacoes=observacoes
        )
        return movimentacao_service.registrar_retirada(db, mov_dados)
    except Exception as e:
        logging.error(f"Erro ao registrar retirada: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/movimentar/devolucao")
async def devolver_processo(
    dados: MovimentacaoDevolucao,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        return movimentacao_service.registrar_devolucao(db, dados)
    except Exception as e:
        logging.error(f"Erro ao registrar devolução: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tipos")
async def listar_tipos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    return configuracao_service.get_tipos_processo(db)

@router.get("/setores")
async def listar_setores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    return configuracao_service.get_setores(db)


