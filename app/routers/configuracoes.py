from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.services import auth_service, configuracao_service
from app.models.usuario import Usuario
from app.schemas.tipo_processo_schema import TipoProcessoCriar, TipoProcessoSchema
from app.schemas.setor_schema import SetorCriar, SetorSchema
from app.schemas.status_processo_schema import StatusProcessoCriar, StatusProcessoSchema
import logging

router = APIRouter(prefix="/api/configuracoes", tags=["Configurações"])

# Tipos de Processo
@router.get("/tipos", response_model=List[TipoProcessoSchema])
async def listar_tipos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    return configuracao_service.get_tipos_processo(db)

@router.post("/tipos", response_model=TipoProcessoSchema, status_code=status.HTTP_201_CREATED)
async def criar_tipo(
    dados: TipoProcessoCriar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.require_admin)
):
    try:
        novo = configuracao_service.criar_tipo_processo(db, dados)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "criar_tipo_processo", f"tipo_processo:{novo.id}",
            f"Tipo '{novo.nome}' criado"
        )
        return novo
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao criar tipo de processo")
        raise HTTPException(status_code=400, detail="Não foi possível criar o tipo de processo.")

@router.put("/tipos/{tipo_id}", response_model=TipoProcessoSchema)
async def editar_tipo(
    tipo_id: int,
    dados: TipoProcessoCriar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.require_admin)
):
    try:
        atualizado = configuracao_service.atualizar_tipo_processo(db, tipo_id, dados)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "editar_tipo_processo", f"tipo_processo:{tipo_id}",
            f"Tipo '{atualizado.nome}' atualizado"
        )
        return atualizado
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao editar tipo de processo %s", tipo_id)
        raise HTTPException(status_code=400, detail="Não foi possível editar o tipo de processo.")

@router.delete("/tipos/{tipo_id}")
async def deletar_tipo(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.require_admin)
):
    try:
        configuracao_service.deletar_tipo_processo(db, tipo_id)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "deletar_tipo_processo", f"tipo_processo:{tipo_id}",
            "Tipo de processo excluído"
        )
        return {"message": "Tipo excluído com sucesso"}
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao deletar tipo de processo %s", tipo_id)
        raise HTTPException(status_code=400, detail="Não foi possível excluir o tipo de processo.")

# Setores
@router.get("/setores", response_model=List[SetorSchema])
async def listar_setores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    return configuracao_service.get_setores(db)

@router.post("/setores", response_model=SetorSchema, status_code=status.HTTP_201_CREATED)
async def criar_setor(
    dados: SetorCriar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.require_admin)
):
    try:
        novo = configuracao_service.criar_setor(db, dados)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "criar_setor", f"setor:{novo.id}",
            f"Setor '{novo.nome}' criado"
        )
        return novo
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao criar setor")
        raise HTTPException(status_code=400, detail="Não foi possível criar o setor.")

@router.put("/setores/{setor_id}", response_model=SetorSchema)
async def editar_setor(
    setor_id: int,
    dados: SetorCriar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.require_admin)
):
    try:
        atualizado = configuracao_service.atualizar_setor(db, setor_id, dados)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "editar_setor", f"setor:{setor_id}",
            f"Setor '{atualizado.nome}' atualizado"
        )
        return atualizado
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao editar setor %s", setor_id)
        raise HTTPException(status_code=400, detail="Não foi possível editar o setor.")

@router.delete("/setores/{setor_id}")
async def deletar_setor(
    setor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.require_admin)
):
    try:
        configuracao_service.deletar_setor(db, setor_id)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "deletar_setor", f"setor:{setor_id}",
            "Setor excluído"
        )
        return {"message": "Setor excluído com sucesso"}
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao deletar setor %s", setor_id)
        raise HTTPException(status_code=400, detail="Não foi possível excluir o setor.")

# Status de Processo
@router.get("/status", response_model=List[StatusProcessoSchema])
async def listar_status(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    return configuracao_service.get_status_processo(db)

@router.post("/status", response_model=StatusProcessoSchema, status_code=status.HTTP_201_CREATED)
async def criar_status(
    dados: StatusProcessoCriar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.require_admin)
):
    try:
        novo = configuracao_service.criar_status_processo(db, dados)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "criar_status", f"status_processo:{novo.id}",
            f"Status '{novo.nome}' criado"
        )
        return novo
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao criar status")
        raise HTTPException(status_code=400, detail="Não foi possível criar o status.")

@router.put("/status/{status_id}", response_model=StatusProcessoSchema)
async def editar_status(
    status_id: int,
    dados: StatusProcessoCriar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.require_admin)
):
    try:
        atualizado = configuracao_service.atualizar_status_processo(db, status_id, dados)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "editar_status", f"status_processo:{status_id}",
            f"Status '{atualizado.nome}' atualizado"
        )
        return atualizado
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao editar status %s", status_id)
        raise HTTPException(status_code=400, detail="Não foi possível editar o status.")

@router.delete("/status/{status_id}")
async def deletar_status(
    status_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.require_admin)
):
    try:
        configuracao_service.deletar_status_processo(db, status_id)
        auth_service.registrar_log_auditoria(
            db, current_user.id, "deletar_status", f"status_processo:{status_id}",
            "Status excluído"
        )
        return {"message": "Status excluído com sucesso"}
    except HTTPException:
        raise
    except Exception:
        logging.exception("Erro ao deletar status %s", status_id)
        raise HTTPException(status_code=400, detail="Não foi possível excluir o status.")
