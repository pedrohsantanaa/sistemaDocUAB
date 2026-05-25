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

# Instalar dependências do sistema necessárias para algumas libs python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o código do backend
COPY app/ ./app/
COPY .env* seed_admin.py ./

# Copiar os arquivos compilados do frontend para uma pasta que o FastAPI possa servir
COPY --from=frontend-build /frontend/dist/ ./static/

# Expor a porta 8000
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
