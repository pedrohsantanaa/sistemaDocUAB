from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.services import auth_service, configuracao_service
from app.models.usuario import Usuario
from app.schemas.tipo_processo_schema import TipoProcessoCriar, TipoProcessoSchema
from app.schemas.setor_schema import SetorCriar, SetorSchema
from app.schemas.status_processo_schema import StatusProcessoCriar, StatusProcessoSchema

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
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    auth_service.is_admin(current_user)
    try:
        return configuracao_service.criar_tipo_processo(db, dados)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/tipos/{tipo_id}", response_model=TipoProcessoSchema)
async def editar_tipo(
    tipo_id: int,
    dados: TipoProcessoCriar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    auth_service.is_admin(current_user)
    try:
        return configuracao_service.atualizar_tipo_processo(db, tipo_id, dados)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/tipos/{tipo_id}")
async def deletar_tipo(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    auth_service.is_admin(current_user)
    try:
        configuracao_service.deletar_tipo_processo(db, tipo_id)
        return {"message": "Tipo excluído com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    auth_service.is_admin(current_user)
    try:
        return configuracao_service.criar_setor(db, dados)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/setores/{setor_id}", response_model=SetorSchema)
async def editar_setor(
    setor_id: int,
    dados: SetorCriar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    auth_service.is_admin(current_user)
    try:
        return configuracao_service.atualizar_setor(db, setor_id, dados)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/setores/{setor_id}")
async def deletar_setor(
    setor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    auth_service.is_admin(current_user)
    try:
        configuracao_service.deletar_setor(db, setor_id)
        return {"message": "Setor excluído com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    auth_service.is_admin(current_user)
    try:
        return configuracao_service.criar_status_processo(db, dados)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/status/{status_id}", response_model=StatusProcessoSchema)
async def editar_status(
    status_id: int,
    dados: StatusProcessoCriar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    auth_service.is_admin(current_user)
    try:
        return configuracao_service.atualizar_status_processo(db, status_id, dados)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/status/{status_id}")
async def deletar_status(
    status_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    auth_service.is_admin(current_user)
    try:
        configuracao_service.deletar_status_processo(db, status_id)
        return {"message": "Status excluído com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
