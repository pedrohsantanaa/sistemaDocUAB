from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.services import processo_service
import logging

router = APIRouter(prefix="/processos")
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def web_listar_processos(
    request: Request, 
    busca: Optional[str] = None, 
    status: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    try:
        processos_encontrados = processo_service.buscar_processos_com_filtros(db, busca, status)
        
        # Calcular estatísticas básicas
        from app.models.processo import Processo
        total_processos = db.query(Processo).count()
        processos_disponiveis = db.query(Processo).filter(Processo.status == "Disponível").count()
        processos_em_posse = db.query(Processo).filter(Processo.status == "Em Posse").count()
        processos_pendentes = db.query(Processo).filter(Processo.status == "Pendente").count()
        
        return templates.TemplateResponse(
            request=request,
            name="processos/dashboard.html",
            context={
                "lista_processos": processos_encontrados,
                "busca_atual": busca,
                "status_atual": status,
                "stats": {
                    "total": total_processos,
                    "disponiveis": processos_disponiveis,
                    "em_posse": processos_em_posse,
                    "pendentes": processos_pendentes
                }
            }
        )
    except Exception as e:
        logging.error(f"Erro ao listar processos: {e}")
        return templates.TemplateResponse(request=request, name="500.html")

@router.get("/{processo_id}/historico")
async def web_historico_processo(
    request: Request, 
    processo_id: int, 
    db: Session = Depends(get_db)
):
    try:
        dados_historico = processo_service.consultar_historico_processo(db, processo_id)
        
        return templates.TemplateResponse(
            request=request,
            name="processos/historico.html",
            context={
                "processo": dados_historico["processo"],
                "movimentacoes": dados_historico["historico"],
                "total": dados_historico["total_movimentacoes"]
            }
        )
    except Exception as e:
        logging.error(f"Erro ao consultar histórico: {e}")
        return templates.TemplateResponse(request=request, name="404.html", context={"mensagem": str(e)})

@router.get("/cadastrar")
async def web_form_cadastrar_processo(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="processos/cadastrar.html"
    )

@router.get("/retirada")
async def web_form_retirada(request: Request, processo_id: Optional[int] = None):
    return templates.TemplateResponse(
        request=request,
        name="processos/retirada.html",
        context={"processo_id": processo_id}
    )

@router.get("/devolucao")
async def web_form_devolucao(request: Request, processo_id: Optional[int] = None, db: Session = Depends(get_db)):
    movimentacao_id = None
    if processo_id:
        # Tentar encontrar a movimentação ativa para este processo
        from app.models.movimentacao import Movimentacao
        mov = db.query(Movimentacao).filter(
            Movimentacao.processo_id == processo_id,
            Movimentacao.data_devolucao == None
        ).first()
        if mov:
            movimentacao_id = mov.id
            
    return templates.TemplateResponse(
        request=request,
        name="processos/devolucao.html",
        context={"processo_id": processo_id, "movimentacao_id": movimentacao_id}
    )

@router.get("/retirar/{processo_id}")
async def web_retirar_processo_direto(request: Request, processo_id: int):
    return RedirectResponse(url=f"/processos/retirada?processo_id={processo_id}")

@router.get("/devolver/{processo_id}")
async def web_devolver_processo_direto(request: Request, processo_id: int):
    return RedirectResponse(url=f"/processos/devolucao?processo_id={processo_id}")

