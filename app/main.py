from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.database.session import engine, Base
from app.routers import processos, auth, usuarios, configuracoes, relatorios
from app.models import processo, movimentacao, usuario, log, tipo_processo, setor, status_processo
import os

# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Gestão Documental - Fomento Tocantins")

# Configurar CORS com origens permitidas explícitas (via ALLOWED_ORIGINS)
_origens = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:8000,http://localhost:8001,http://localhost",
)
ALLOWED_ORIGINS = [o.strip() for o in _origens.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cabeçalhos de segurança HTTP (V06)
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; "
        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
    )
    return response

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
        # Evita capturar rotas que começam com /api (endpoint inexistente → 404)
        if full_path.startswith("api"):
            return JSONResponse(
                status_code=404, content={"detail": "Endpoint não encontrado"}
            )
            
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
