# Guia de Manutenção - Sistema de Gestão Documental (Fomento TO)

Este documento serve como guia didático para futuros desenvolvedores que realizarão a manutenção deste sistema.

## 🏗️ Arquitetura do Projeto

O sistema segue uma arquitetura em camadas para garantir a separação de responsabilidades e facilitar a manutenção:

1.  **Modelos (`app/models/`)**: Representam as tabelas do banco de dados e seus relacionamentos (SQLAlchemy).
2.  **Esquemas (`app/schemas/`)**: Validação de entrada e saída de dados (Pydantic).
3.  **Serviços (`app/services/`)**: Contém a "Regra de Negócio". É onde a lógica pesada acontece.
4.  **Roteadores (`app/routers/`)**: Define os pontos de entrada (Endpoints) da API e gerencia as requisições HTTP.
5.  **Banco de Dados (`app/database/`)**: Configuração da conexão e gerenciamento de sessões.

## 🧹 Princípios de Clean Code Aplicados

- **Nomenclatura Semântica**: Funções e variáveis possuem nomes claros que descrevem sua finalidade (ex: `registrar_entrada_processo` em vez de `add_proc`).
- **Funções Pequenas**: Cada função deve fazer apenas uma coisa e fazê-la bem.
- **Tratamento de Exceções**: Uso sistemático de `try/except` para capturar erros e retornar respostas HTTP claras.
- **Injeção de Dependência**: O banco de dados é injetado nas funções para facilitar testes.

## 🛠️ Como dar manutenção

### Adicionar um novo campo em uma tabela:
1. Altere o modelo em `app/models/`.
2. Atualize o esquema em `app/schemas/`.
3. Verifique se o serviço em `app/services/` precisa lidar com esse novo campo.

### Criar uma nova funcionalidade:
1. Comece pelo Modelo (Banco de Dados).
2. Crie o Serviço (Lógica).
3. Crie o Roteador (API).
4. Integre no Frontend.

## 🐳 Docker & Infraestrutura
O sistema utiliza Docker para facilitar o ambiente de desenvolvimento:
- `db`: PostgreSQL 15.
- `web`: FastAPI + Frontend compilado.
- `pgadmin`: Interface visual para o banco de dados.

---
*Documentação gerada em Maio de 2026 para a Agência de Fomento do Estado do Tocantins.*
