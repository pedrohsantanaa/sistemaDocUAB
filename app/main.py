from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database.session import engine, Base
from app.routers import processos, auth, usuarios, configuracoes, relatorios
from app.models import processo, movimentacao, usuario, log, tipo_processo, setor
import os

# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Gestão de Processos Físicos")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir roteadores da API
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(processos.router)
app.include_router(configuracoes.router)
app.include_router(relatorios.router)

# Servir arquivos estáticos do frontend (pasta 'static' gerada no Dockerfile)
if os.path.exists("static"):
    # Montar a pasta de assets explicitamente
    if os.path.exists("static/assets"):
        app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Evita capturar rotas que começam com /api
        if full_path.startswith("api"):
            return None # Deixa o FastAPI tratar via routers
            
        # Se o caminho for um arquivo real em static, serve ele (ex: favicon.svg)
        file_path = os.path.join("static", full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Caso contrário, serve o index.html para o Vue Router lidar com o caminho
        return FileResponse("static/index.html")
else:
    @app.get("/")
    async def root():
        return {"message": "SistemaDocUAB API está ativa. Frontend não encontrado.", "docs": "/docs"}
