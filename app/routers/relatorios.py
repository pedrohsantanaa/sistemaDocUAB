from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database.session import get_db
from app.services import auth_service
from app.models.usuario import Usuario
from app.models.processo import Processo
from app.models.movimentacao import Movimentacao
import logging

router = APIRouter(prefix="/api/relatorios", tags=["Relatórios"])

@router.get("/")
async def get_relatorios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth_service.get_current_user)
):
    auth_service.is_admin(current_user)
    
    try:
        # 1. Status Distribution
        status_counts = db.query(Processo.status, func.count(Processo.id)).group_by(Processo.status).all()
        status_data = {s[0]: s[1] for s in status_counts}

        # 2. Movements last 7 days
        today = datetime.now().date()
        last_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        movements_by_day = []

        for day in last_7_days:
            count = db.query(Movimentacao).filter(func.date(Movimentacao.data_retirada) == day).count()
            movements_by_day.append({
                "data": day.strftime("%Y-%m-%d"),
                "label": day.strftime("%d/%m"),
                "total": count
            })

        # 3. KPI Metrics
        total = db.query(Processo).count()
        em_posse = db.query(Processo).filter(Processo.status == "Em Posse").count()
        disponivel = db.query(Processo).filter(Processo.status == "Disponível").count()
        pendente = db.query(Processo).filter(Processo.status == "Pendente").count()

        # 4. Recent Movements
        recent_movs = db.query(Movimentacao).order_by(Movimentacao.data_retirada.desc()).limit(10).all()
        
        # Formatar movimentações recentes para JSON
        recentes_formatados = []
        for m in recent_movs:
            recentes_formatados.append({
                "id": m.id,
                "processo": m.processo.numero_contrato if m.processo else "N/A",
                "cliente": m.processo.nome_cliente if m.processo else "N/A",
                "usuario": m.usuario.nome if m.usuario else "Sistema",
                "setor_destino": m.setor_destino,
                "data_retirada": m.data_retirada.isoformat() if m.data_retirada else None,
                "data_devolucao": m.data_devolucao.isoformat() if m.data_devolucao else None
            })

        return {
            "status_distribution": status_data,
            "movements_last_7_days": movements_by_day,
            "stats": {
                "total": total,
                "em_posse": em_posse,
                "disponivel": disponivel,
                "pendente": pendente
            },
            "recent_movements": recentes_formatados
        }
    except Exception as e:
        logging.error(f"Erro ao gerar relatórios: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar relatórios")
