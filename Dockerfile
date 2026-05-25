# Utilizar imagem base oficial do Python (versão slim para menor tamanho)
FROM python:3.10-slim

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar arquivo de dependências para o contêiner
COPY requirements.txt .

# Atualizar pip e instalar dependências sem usar cache para reduzir tamanho da imagem
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo o código fonte e a estrutura de diretórios para o contêiner
COPY . .

# Expor a porta 8000 para acesso externo
EXPOSE 8000

# Comando para iniciar o servidor FastAPI via Uvicorn no modo host global
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
