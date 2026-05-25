from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services import movimentacao_service
from app.schemas.movimentacao_schema import MovimentacaoCriar, MovimentacaoDevolucao
import logging

from app.schemas.processo_schema import ProcessoCriar
from app.services import processo_service, auth_service, configuracao_service
from app.schemas.tipo_processo_schema import TipoProcessoCriar
from app.schemas.setor_schema import SetorCriar
from app.models.usuario import Usuario

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/processos/cadastrar")
async def web_cadastrar_processo(
    request: Request,
    nome_cliente: str = Form(...),
    cpf_cnpj: str = Form(...),
    numero_contrato: str = Form(...),
    tipo_processo: str = Form(...),
    setor_responsavel: str = Form(...),
    status: str = Form("Disponível"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
    
    try:
        dados = ProcessoCriar(
            nome_cliente=nome_cliente,
            cpf_cnpj=cpf_cnpj,
            numero_contrato=numero_contrato,
            tipo_processo=tipo_processo,
            setor_responsavel=setor_responsavel,
            status=status
        )
        processo_service.criar_processo(db, dados)
        return RedirectResponse(url="/processos?msg=Processo cadastrado com sucesso", status_code=303)
    except Exception as e:
        logging.error(f"Erro ao cadastrar processo: {e}")
        return templates.TemplateResponse(
            request=request, 
            name="processos/cadastrar.html", 
            context={"erro": str(e), "usuario_logado": current_user}
        )

@router.post("/processos/movimentar/retirada")
async def web_retirar_processo(
    request: Request,
    processo_id: int = Form(...),
    setor_destino: str = Form(...),
    observacoes: str = Form(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
    
    try:
        mov_dados = MovimentacaoCriar(
            processo_id=processo_id,
            usuario_id=current_user.id,
            setor_destino=setor_destino,
            observacoes=observacoes
        )
        movimentacao_service.registrar_retirada(db, mov_dados)
        
        return RedirectResponse(url="/processos?msg=Retirada registrada com sucesso", status_code=303)
        
    except Exception as e:
        logging.error(f"Erro ao registrar retirada: {e}")
        return templates.TemplateResponse(
            request=request, 
            name="processos/retirada.html", 
            context={"erro": str(e), "processo_id": processo_id, "usuario_logado": current_user}
        )

@router.post("/processos/movimentar/devolucao")
async def web_devolver_processo(
    request: Request,
    movimentacao_id: int = Form(...),
    novo_status: str = Form(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
        
    try:
        dados = MovimentacaoDevolucao(
            movimentacao_id=movimentacao_id,
            novo_status_processo=novo_status
        )
        movimentacao_service.registrar_devolucao(db, dados)
        
        return RedirectResponse(url="/processos?msg=Devolução registrada com sucesso", status_code=303)
        
    except Exception as e:
        logging.error(f"Erro ao registrar devolução: {e}")
        return templates.TemplateResponse(
            request=request, 
            name="processos/devolucao.html", 
            context={"erro": str(e), "movimentacao_id": movimentacao_id, "usuario_logado": current_user}
        )

@router.get("/relatorios")
async def web_relatorios(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
    
    auth_service.is_admin(current_user)
    
    try:
        from app.models.processo import Processo
        from app.models.movimentacao import Movimentacao
        from datetime import datetime, timedelta
        from sqlalchemy import func

        # 1. Status Distribution (Donut Chart)
        status_counts = db.query(Processo.status, func.count(Processo.id)).group_by(Processo.status).all()
        status_labels = [s[0] for s in status_counts]
        status_data = [s[1] for s in status_counts]

        # 2. Movements last 7 days (Line Chart)
        today = datetime.now().date()
        last_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        movements_by_day = []
        labels_days = []

        for day in last_7_days:
            count = db.query(Movimentacao).filter(func.date(Movimentacao.data_retirada) == day).count()
            movements_by_day.append(count)
            labels_days.append(day.strftime("%d/%m"))

        # 3. KPI Metrics
        total = db.query(Processo).count()
        em_posse = db.query(Processo).filter(Processo.status == "Em Posse").count()
        disponivel = db.query(Processo).filter(Processo.status == "Disponível").count()
        pendente = db.query(Processo).filter(Processo.status == "Pendente").count()

        # 4. Recent Movements
        recent_movs = db.query(Movimentacao).order_by(Movimentacao.data_retirada.desc()).limit(5).all()

        return templates.TemplateResponse(
            request=request, 
            name="relatorios.html",
            context={
                "status_labels": status_labels,
                "status_data": status_data,
                "labels_days": labels_days,
                "movements_data": movements_by_day,
                "usuario_logado": current_user,
                "stats": {
                    "total": total,
                    "em_posse": em_posse,
                    "disponivel": disponivel,
                    "pendente": pendente
                },
                "recent_movs": recent_movs
            }
        )
    except Exception as e:
        logging.error(f"Erro ao carregar relatórios: {e}")
        return templates.TemplateResponse(request=request, name="500.html", context={"usuario_logado": current_user})

# --- Configurações (Admin) ---

@router.get("/configuracoes")
async def web_configuracoes(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
    
    auth_service.is_admin(current_user)
    
    tipos = configuracao_service.get_tipos_processo(db)
    setores = configuracao_service.get_setores(db)
    
    return templates.TemplateResponse(
        request=request,
        name="configuracoes.html",
        context={
            "titulo_pagina": "Configurações",
            "usuario_logado": current_user,
            "tipos": tipos,
            "setores": setores
        }
    )

# Tipos de Processo
@router.post("/configuracoes/tipos")
async def web_criar_tipo(
    nome: str = Form(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
    auth_service.is_admin(current_user)
    
    try:
        configuracao_service.criar_tipo_processo(db, TipoProcessoCriar(nome=nome))
        return RedirectResponse(url="/configuracoes?msg=Tipo criado com sucesso", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/configuracoes?erro={str(e)}", status_code=303)

@router.post("/configuracoes/tipos/editar/{tipo_id}")
async def web_editar_tipo(
    tipo_id: int,
    nome: str = Form(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
    auth_service.is_admin(current_user)
    
    try:
        configuracao_service.atualizar_tipo_processo(db, tipo_id, TipoProcessoCriar(nome=nome))
        return RedirectResponse(url="/configuracoes?msg=Tipo atualizado com sucesso", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/configuracoes?erro={str(e)}", status_code=303)

@router.get("/configuracoes/tipos/deletar/{tipo_id}")
async def web_deletar_tipo(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
    auth_service.is_admin(current_user)
    
    try:
        configuracao_service.deletar_tipo_processo(db, tipo_id)
        return RedirectResponse(url="/configuracoes?msg=Tipo excluído com sucesso", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/configuracoes?erro={str(e)}", status_code=303)

# Setores
@router.post("/configuracoes/setores")
async def web_criar_setor(
    nome: str = Form(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
    auth_service.is_admin(current_user)
    
    try:
        configuracao_service.criar_setor(db, SetorCriar(nome=nome))
        return RedirectResponse(url="/configuracoes?msg=Setor criado com sucesso", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/configuracoes?erro={str(e)}", status_code=303)

@router.post("/configuracoes/setores/editar/{setor_id}")
async def web_editar_setor(
    setor_id: int,
    nome: str = Form(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
    auth_service.is_admin(current_user)
    
    try:
        configuracao_service.atualizar_setor(db, setor_id, SetorCriar(nome=nome))
        return RedirectResponse(url="/configuracoes?msg=Setor atualizado com sucesso", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/configuracoes?erro={str(e)}", status_code=303)

@router.get("/configuracoes/setores/deletar/{setor_id}")
async def web_deletar_setor(
    setor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login")
    auth_service.is_admin(current_user)
    
    try:
        configuracao_service.deletar_setor(db, setor_id)
        return RedirectResponse(url="/configuracoes?msg=Setor excluído com sucesso", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/configuracoes?erro={str(e)}", status_code=303)


