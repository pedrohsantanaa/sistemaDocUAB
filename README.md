# Sistema DocUAB - Gestão Documental e Rastreabilidade

Sistema moderno para controle de movimentação, arquivamento e rastreabilidade de processos físicos. Desenvolvido para oferecer eficiência, segurança e uma interface intuitiva.

## 🛠️ Stack Tecnológica

### Backend
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Banco de Dados:** PostgreSQL 15
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
- **Autenticação:** JWT (JSON Web Tokens) com segurança baseada em roles (RBAC)
- **Validação:** Pydantic v2

### Frontend
- **Framework:** [Vue.js 3](https://vuejs.org/) (Composition API)
- **Ferramenta de Build:** Vite
- **UI Components:** [PrimeVue v4](https://primevue.org/)
- **Estilização:** [Tailwind CSS 4](https://tailwindcss.com/)
- **Gerenciamento de Estado:** Pinia
- **Gráficos:** Chart.js

### Infraestrutura
- **Containerização:** Docker & Docker Compose (Multi-stage builds)
- **Servidor:** Uvicorn

## ✨ Funcionalidades Principais

- **📦 Gestão de Processos:** Cadastro, edição e acompanhamento de processos físicos.
- **🔄 Fluxo de Movimentação:** Registro detalhado de entradas, saídas e transferências entre setores.
- **🕒 Histórico Completo:** Rastreabilidade total de cada documento com log de alterações.
- **📊 Dashboard Inteligente:** Visualização de KPIs, status de processos e volume de movimentações via gráficos interativos.
- **👥 Controle de Acesso (RBAC):** Gestão de usuários com diferentes níveis de permissão (Admin e Usuário).
- **⚙️ Configurações Dinâmicas:** Gerenciamento de setores, tipos de processos e status de processos.

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Docker e Docker Compose **OU**
- Python 3.10+ e Node.js 20+

### 🐳 Via Docker (Recomendado)

A forma mais rápida de subir o ambiente completo (Backend, Frontend, Banco de Dados e pgAdmin):

```bash
docker-compose up --build -d
```

- **Aplicação:** `http://localhost:8001`
- **pgAdmin:** `http://localhost:5050` (Login: `admin@admin.com` / `admin`)
- **Documentação API (Swagger):** `http://localhost:8001/docs`

### 💻 Desenvolvimento Local (Sem Docker)

#### 1. Banco de Dados
Certifique-se de ter um PostgreSQL rodando e crie um banco chamado `sistemadocuab`.

#### 2. Backend (FastAPI)
```bash
# Entrar na pasta raiz
cd sistemaDocUAB

# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate # Windows

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env
cp .env.example .env # Caso exista, ou crie manualmente

# Executar script de semente (Admin inicial)
PYTHONPATH=. python seed_admin.py

# Iniciar o servidor
uvicorn app.main:app --reload
```

#### 3. Frontend (Vue.js)
```bash
# Entrar na pasta do frontend
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```
Acesse `http://localhost:5173` (ou a porta indicada pelo Vite).

## 📁 Estrutura do Projeto

```text
├── app/                # Backend FastAPI
│   ├── database/       # Conexão e sessão do banco
│   ├── models/         # Modelos SQLAlchemy
│   ├── routers/        # Rotas da API
│   ├── schemas/        # Schemas Pydantic
│   ├── services/       # Lógica de negócio
│   └── templates/      # (Opcional) Templates legados
├── frontend/           # Frontend Vue.js 3
│   ├── src/
│   │   ├── api/        # Integração com backend (Axios)
│   │   ├── components/ # Componentes reutilizáveis
│   │   ├── stores/     # Estado global (Pinia)
│   │   └── views/      # Páginas da aplicação
├── scripts/            # Scripts utilitários (Backup, etc)
├── Dockerfile          # Build multi-stage
└── docker-compose.yml  # Orquestração de serviços
```

## 🔒 Segurança

- **JWT em Cookies HttpOnly:** Proteção contra XSS.
- **Hashing de Senhas:** Utiliza `bcrypt` para armazenamento seguro.
- **CORS:** Configurado para aceitar requisições apenas de origens autorizadas.

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).

---
Desenvolvido para **Fomento Tocantins / UAB**.
