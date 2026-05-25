"""
Módulo de Configuração de Banco de Dados
Gerencia a conexão com o PostgreSQL e a criação de sessões para o SQLAlchemy.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Define a URL do banco. Prioriza a variável de ambiente DATABASE_URL.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/sistemadocuab")

# O 'engine' é o ponto central de conexão com o banco.
# Em PostgreSQL não precisamos do connect_args do SQLite.
engine = create_engine(DATABASE_URL)

# SessionLocal é uma classe que criará instâncias de sessões de banco de dados.
# Estas sessões serão usadas para realizar operações (Insert, Update, Select).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base é a classe que todos os modelos herdarão para serem mapeados pelo ORM.
Base = declarative_base()

def get_db():
    """
    Gerador de Sessão de Banco de Dados (Dependency Injection).
    Garante que a conexão seja aberta no início da requisição e fechada ao final.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
