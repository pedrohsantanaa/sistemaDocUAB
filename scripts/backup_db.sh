#!/bin/bash

# Script de Backup - Agência de Fomento do Tocantins
# Este script gera um arquivo .sql contendo todos os dados e estrutura do banco.

# Configurações
CONTAINER_NAME="sistema_processos_db"
DB_USER="postgres"
DB_NAME="sistemadocuab"
BACKUP_DIR="./backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
FILE_NAME="backup_${DB_NAME}_${DATE}.sql"

# Cria a pasta de backups se não existir
mkdir -p $BACKUP_DIR

echo "🚀 Iniciando backup do banco de dados..."

# Executa o pg_dump dentro do container e salva o resultado fora dele
docker exec $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/$FILE_NAME

# Verifica se o comando anterior deu certo
if [ $? -eq 0 ]; then
  echo "✅ Backup concluído com sucesso!"
  echo "📂 Arquivo salvo em: $BACKUP_DIR/$FILE_NAME"
  
  # Opcional: Remove backups com mais de 30 dias para economizar espaço
  # find $BACKUP_DIR -type f -name "*.sql" -mtime +30 -delete
else
  echo "❌ Erro ao realizar o backup!"
  exit 1
fi
