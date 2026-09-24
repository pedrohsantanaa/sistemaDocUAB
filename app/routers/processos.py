from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.session import get_db
from app.services import processo_service, auth_service, movimentacao_service
from app.models.usuario import Usuario
from app.schemas.processo_schema import ProcessoCriar, ProcessoSchema
from app.schemas.movimentacao_schema import MovimentacaoCriar, MovimentacaoDevolucao
import logging

router = APIRouter(prefix="/api/processos", tags=["Processos"])

def _serializar_movimentacao(mov):
    """Converte a movimentação em dict antes do commit do log de auditoria.
    Esse commit expira os objetos da sessão e a resposta sairia vazia ({})."""
    return {
        "id": mov.id,
        "processo_id": mov.processo_id,
        "usuario_id": mov.usuario_id,
        "setor_destino": mov.setor_destino,
        "observacoes": mov.observacoes,
        "data_retirada": mov.data_retirada,
        "data_devolucao": mov.data_devolucao,
    }

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

    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao listar processos")
        raise HTTPException(status_code=500, detail="Erro interno ao listar processos.")

@router.post("/cadastrar", status_code=status.HTTP_201_CREATED)
async def cadastrar_processo(
    dados: ProcessoCriar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        novo_processo = processo_service.criar_processo(db, dados, current_user)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "criar_processo", f"processo:{novo_processo.id}",
            f"Processo '{novo_processo.numero_contrato}' cadastrado"
        )
        return ProcessoSchema.from_orm(novo_processo)
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao cadastrar processo")
        raise HTTPException(status_code=400, detail="Não foi possível cadastrar o processo.")

@router.get("/{processo_id}/historico")
async def historico_processo(
    processo_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        dados_historico = processo_service.consultar_historico_processo(
            db, processo_id, current_user
        )
        return dados_historico
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao consultar histórico do processo %s", processo_id)
        raise HTTPException(status_code=404, detail="Processo não localizado.")

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
        mov = movimentacao_service.registrar_retirada(db, mov_dados, current_user)
        resposta = _serializar_movimentacao(mov)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "retirada_processo", f"processo:{processo_id}",
            f"Retirada para o setor '{setor_destino}'"
        )
        return resposta
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao registrar retirada do processo %s", processo_id)
        raise HTTPException(status_code=400, detail="Não foi possível registrar a retirada.")

@router.post("/movimentar/devolucao")
async def devolver_processo(
    dados: MovimentacaoDevolucao,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    try:
        mov = movimentacao_service.registrar_devolucao(db, dados, current_user)
        resposta = _serializar_movimentacao(mov)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "devolucao_processo",
            f"processo:{resposta['processo_id']}",
            "Devolução registrada"
        )
        return resposta
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao registrar devolução")
        raise HTTPException(status_code=400, detail="Não foi possível registrar a devolução.")

