from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database.session import engine, Base
from app.routers import processos, views
from app.models import processo, movimentacao, usuario, log

# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Gestão de Processos Físicos")

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Incluir roteadores
app.include_router(processos.router)
app.include_router(views.router)

@app.get("/")
async def root():
    return {"message": "Bem-vindo ao Sistema de Gestão de Processos Físicos. Acesse /processos para o dashboard."}
