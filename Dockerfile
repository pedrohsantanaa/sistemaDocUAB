# Estágio 1: Build do Frontend (Vue.js)
FROM node:20-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Estágio 2: Backend (FastAPI)
FROM python:3.10-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o build do frontend do estágio anterior
# (o app/main.py serve o SPA a partir do diretório 'static')
COPY --from=frontend-build /frontend/dist/ /app/static/

# Copiar o código do backend (o pacote Python continua se chamando 'app')
COPY backend/app/ ./app/
COPY backend/seed_admin.py ./
COPY backend/entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Usuário não privilegiado — a aplicação não roda como root (V03)
RUN addgroup --system appuser && adduser --system --group appuser \
    && chown -R appuser:appuser /app
USER appuser

# Comando para iniciar o servidor (semeia o banco e sobe o uvicorn)
CMD ["./entrypoint.sh"]
