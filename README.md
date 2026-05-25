# Sistema DocUAB - Gestão de Processos Físicos

Sistema para controle de movimentação e rastreabilidade de arquivos e processos físicos, desenvolvido com foco em integridade de dados e facilidade de uso.

## 🚀 Tecnologias

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Banco de Dados:** PostgreSQL com [SQLAlchemy ORM](https://www.sqlalchemy.org/)
- **Frontend:** Jinja2 Templates, Bootstrap 5 e FontAwesome
- **Autenticação:** JWT (JSON Web Tokens) com Cookies seguros
- **Containerização:** Docker e Docker Compose

## ✨ Funcionalidades Principais

- **Dashboard de Processos:** Visão geral de todos os processos com filtros por status e busca textual.
- **Gestão de Movimentações:** Registro simplificado de retirada e devolução de processos físicos.
- **Rastreabilidade (Histórico):** Log detalhado de quem retirou, quando devolveu e observações de cada processo.
- **Relatórios & KPIs:** Gráficos interativos (Chart.js) mostrando a distribuição de status e volume de movimentações.
- **Níveis de Acesso (RBAC):**
  - **Administrador:** Gerenciamento de usuários, visualização de relatórios e controle total.
  - **Usuário Comum:** Consulta de processos e registro de movimentações.
- **Segurança:** Senhas criptografadas com `bcrypt` e proteção de rotas via dependências do FastAPI.

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.10 ou superior
- Docker & Docker Compose (Opcional para execução em container)

### Passo a Passo (Local)

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd sistemaDocUAB
   ```

2. **Crie um ambiente virtual e instale as dependências:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # ou
   .\venv\Scripts\activate  # Windows
   
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente:**
   Crie um arquivo `.env` na raiz do projeto (opcional, utiliza valores padrão se ausente):
   ```env
   SECRET_KEY=sua-chave-secreta-aqui
   ALGORITHM=HS256
   DATABASE_URL=postgresql://postgres:postgres@db:5432/sistemadocuab
   ```

4. **Crie o usuário administrador inicial:**
   ```bash
   PYTHONPATH=. python3 seed_admin.py
   ```
   *Credenciais padrão:* `admin@docuab.com` / `admin123`

5. **Inicie o servidor:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Acesse: `http://localhost:8000`

### Usando Docker

```bash
docker-compose up --build -d
```
O sistema estará disponível em `http://localhost:8001`.

## 📁 Estrutura do Projeto

```text
├── app/
│   ├── database/    # Configuração da conexão e sessão do banco
│   ├── models/      # Definição das tabelas (SQLAlchemy)
│   ├── schemas/     # Validação de dados (Pydantic)
│   ├── services/    # Regras de negócio e lógica complexa
│   ├── routers/     # Controladores e rotas da API/Web
│   ├── static/      # Arquivos estáticos (CSS, JS, Imagens)
│   └── templates/   # Páginas HTML (Jinja2)
├── data/            # Local para backups ou logs (não mais usado para SQLite)
├── Dockerfile       # Receita da imagem Docker
├── docker-compose.yml
└── seed_admin.py    # Script de criação do admin inicial
```

## 🔐 Segurança

O sistema utiliza cookies `HttpOnly` para armazenar o token JWT, prevenindo ataques de XSS. O acesso a rotas sensíveis como `/usuarios` e `/relatorios` é restrito exclusivamente ao perfil `admin`.

---
Desenvolvido para **UAB - Universidade Aberta do Brasil**.
