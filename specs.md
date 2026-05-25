# specs.md
**Sistema de Gestão de Arquivos e Controle de Processos Físicos**
**Especificações Técnicas Granulares**

---

### 1. Configuração de Banco de Dados

`/app/database/session.py`
- ação: criar
- descrição: Configura a conexão com o banco de dados SQLite utilizando o SQLAlchemy, lendo a URL do banco a partir das variáveis de ambiente e disponibilizando um gerador de sessões para injeção de dependência.
- pseudocódigo:
    ```text
    IMPORTAR sqlalchemy, sessionmaker
    IMPORTAR variaveis_de_ambiente (DATABASE_URL)

    CRIAR engine_banco_dados COM sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": Falso})
    CRIAR SessionLocal COM sessionmaker(bind=engine_banco_dados, autocommit=Falso, autoflush=Falso)

    FUNÇÃO obter_sessao_banco():
        sessao = INSTANCIAR SessionLocal()
        TENTAR:
            ENTREGAR sessao (yield)
        FINALMENTE:
            FECHAR sessao
    ```

---

### 2. Definição de Modelos (ORM)

`/app/models/processo.py`
- ação: criar
- descrição: Mapeia a tabela `processos` no banco de dados, estabelecendo as colunas, tipos de dados estritos e valores padrão para refletir as entidades físicas.
- pseudocódigo:
    ```text
    IMPORTAR Base do sqlalchemy
    IMPORTAR Tipos (Integer, String, DateTime, Enum)

    CLASSE Processo(Base):
        DEFINIR NOME_TABELA = "processos"
        
        COLUNA id: Inteiro, Chave Primária, Auto Incremento
        COLUNA nome_cliente: String, Não Nulo
        COLUNA cpf_cnpj: String, Não Nulo, Único
        COLUNA numero_contrato: String, Não Nulo, Único
        COLUNA tipo_processo: String, Não Nulo
        COLUNA status: Enum("Disponível", "Em Posse", "Pendente", "Liquidado", "Arquivado"), Padrão="Disponível", Não Nulo
        COLUNA data_entrada: DateTime, Padrão=DataHoraAtual, Não Nulo
        COLUNA setor_responsavel: String, Não Nulo
        
        RELACIONAMENTO movimentacoes = Relaciona("Movimentacao", cascade="all, delete-orphan")
    ```

`/app/models/movimentacao.py`
- ação: criar
- descrição: Mapeia a tabela `movimentacoes`, registrando a chave estrangeira do processo e do usuário para garantir a rastreabilidade (log de uso) descrita nos requisitos.
- pseudocódigo:
    ```text
    IMPORTAR Base do sqlalchemy
    IMPORTAR Tipos (Integer, String, DateTime, ForeignKey)

    CLASSE Movimentacao(Base):
        DEFINIR NOME_TABELA = "movimentacoes"
        
        COLUNA id: Inteiro, Chave Primária, Auto Incremento
        COLUNA processo_id: Inteiro, Chave Estrangeira("processos.id"), Não Nulo
        COLUNA usuario_id: Inteiro, Chave Estrangeira("usuarios.id"), Não Nulo
        COLUNA data_retirada: DateTime, Padrão=DataHoraAtual, Não Nulo
        COLUNA data_devolucao: DateTime, Nulo
        COLUNA setor_destino: String, Não Nulo
        COLUNA observacoes: String, Nulo
    ```

---

### 3. Validação de Dados (Schemas)

`/app/schemas/movimentacao_schema.py`
- ação: criar
- descrição: Define as estruturas Pydantic para validar estritamente as requisições HTTP de entrada ao registrar uma movimentação.
- pseudocódigo:
    ```text
    IMPORTAR BaseModel do pydantic

    CLASSE MovimentacaoCriar(BaseModel):
        ATRIBUTO processo_id: Inteiro
        ATRIBUTO usuario_id: Inteiro
        ATRIBUTO setor_destino: String
        ATRIBUTO observacoes: String Opcional

        VALIDADOR_PADRAO: 
            SE setor_destino VAZIO:
                LEVANTAR ERRO_VALIDACAO("Setor de destino é obrigatório")

    CLASSE MovimentacaoDevolucao(BaseModel):
        ATRIBUTO movimentacao_id: Inteiro
        ATRIBUTO novo_status_processo: Enum("Disponível", "Liquidado", "Arquivado")
    ```

---

### 4. Camada de Serviço (Regras de Negócio)

`/app/services/movimentacao_service.py`
- ação: criar
- descrição: Implementa as lógicas transacionais, garantindo que as regras de negócio de retirada e devolução sejam respeitadas, alterando o status do processo de forma atômica.
- pseudocódigo:
    ```text
    IMPORTAR sqlalchemy.Session
    IMPORTAR Modelos (Processo, Movimentacao)
    IMPORTAR Schemas (MovimentacaoCriar, MovimentacaoDevolucao)

    FUNÇÃO registrar_retirada(sessao_db: Session, dados: MovimentacaoCriar):
        processo = BUSCAR Processo ONDE id == dados.processo_id
        
        SE processo É NULO:
            LEVANTAR ExcecaoHttp(404, "Processo não encontrado")
            
        SE processo.status DIFERENTE DE "Disponível":
            LEVANTAR ExcecaoHttp(400, "Processo indisponível para retirada")
            
        NOVA_MOVIMENTACAO = Movimentacao(
            processo_id = dados.processo_id,
            usuario_id = dados.usuario_id,
            setor_destino = dados.setor_destino,
            observacoes = dados.observacoes
        )
        
        processo.status = "Em Posse"
        
        sessao_db.adicionar(NOVA_MOVIMENTACAO)
        sessao_db.atualizar(processo)
        sessao_db.confirmar_transacao()
        
        RETORNAR NOVA_MOVIMENTACAO

    FUNÇÃO registrar_devolucao(sessao_db: Session, dados: MovimentacaoDevolucao):
        mov = BUSCAR Movimentacao ONDE id == dados.movimentacao_id E data_devolucao É NULO
        
        SE mov É NULO:
            LEVANTAR ExcecaoHttp(404, "Movimentação ativa não encontrada")
            
        processo = BUSCAR Processo ONDE id == mov.processo_id
        
        mov.data_devolucao = DataHoraAtual
        processo.status = dados.novo_status_processo
        
        sessao_db.atualizar(mov)
        sessao_db.atualizar(processo)
        sessao_db.confirmar_transacao()
        
        RETORNAR mov
    ```

`/app/services/processo_service.py`
- ação: criar
- descrição: Responsável por gerenciar o ciclo de vida e pesquisa dos processos, abstraindo as queries do banco.
- pseudocódigo:
    ```text
    IMPORTAR sqlalchemy.Session
    IMPORTAR Modelos (Processo)

    FUNÇÃO consultar_historico_processo(sessao_db: Session, id_processo: Inteiro):
        processo = BUSCAR Processo ONDE id == id_processo
        
        SE processo É NULO:
            LEVANTAR ExcecaoHttp(404, "Processo não encontrado")
            
        historico = BUSCAR LISTA DE Movimentacao ONDE processo_id == id_processo ORDENADO POR data_retirada DESCENDENTE
        
        quantidade_movimentacoes = TAMANHO(historico)
        
        RETORNAR {
            "processo": processo,
            "total_movimentacoes": quantidade_movimentacoes,
            "historico": historico
        }
    ```

---

### 5. Camada de Apresentação (Controladores Web)

`/app/routers/views.py`
- ação: criar
- descrição: Recebe as requisições HTTP do cliente, orquestra a injeção da sessão do banco, chama a camada de serviço correspondente e renderiza os templates do Jinja2 com as respostas.
- pseudocódigo:
    ```text
    IMPORTAR APIRouter, Request, Depends do fastapi
    IMPORTAR Jinja2Templates do fastapi.templating
    IMPORTAR movimentacao_service, obter_sessao_banco

    ROTEADOR = INSTANCIAR APIRouter()
    TEMPLATES = INSTANCIAR Jinja2Templates(diretorio="app/templates")

    ROTA POST ("/processos/movimentar/retirada")
    FUNÇÃO web_retirar_processo(requisicao: Request, dados_formulario: Formulario, sessao_db = INJETAR obter_sessao_banco):
        TENTAR:
            mov_dados = MAPEAR dados_formulario PARA MovimentacaoCriar
            movimentacao_service.registrar_retirada(sessao_db, mov_dados)
            
            MENSAGEM_SUCESSO = "Retirada registrada com sucesso."
            REDIRECIONAR PARA "/processos" COM MENSAGEM_SUCESSO
            
        CAPTURAR ExcecaoHttp COMO erro:
            MENSAGEM_ERRO = erro.detalhe
            RETORNAR TEMPLATES.renderizar(
                "processos/retirada.html", 
                contexto={"request": requisicao, "erro": MENSAGEM_ERRO}
            )
    ```

`/app/routers/processos.py`
- ação: criar
- descrição: Controlador responsável por interceptar as rotas de listagem e histórico de processos. Extrai os parâmetros de consulta (query parameters) da URL, consulta o banco de dados via camada de serviço e injeta os resultados no template do dashboard.
- pseudocódigo:
    ```text
    IMPORTAR APIRouter, Request, Depends do fastapi
    IMPORTAR Jinja2Templates do fastapi.templating
    IMPORTAR processo_service, obter_sessao_banco
    IMPORTAR sqlalchemy.Session

    ROTEADOR = INSTANCIAR APIRouter(prefix="/processos")
    TEMPLATES = INSTANCIAR Jinja2Templates(diretorio="app/templates")

    ROTA GET ("/")
    FUNÇÃO web_listar_processos(requisicao: Request, busca: String Opcional, status: String Opcional, sessao_db: Session = INJETAR obter_sessao_banco):
        TENTAR:
            processos_encontrados = processo_service.buscar_processos_com_filtros(sessao_db, busca, status)
            
            RETORNAR TEMPLATES.renderizar(
                "processos/dashboard.html",
                contexto={
                    "request": requisicao,
                    "lista_processos": processos_encontrados,
                    "busca_atual": busca,
                    "status_atual": status
                }
            )
        CAPTURAR Excecao COMO erro:
            REGISTRAR_LOG(erro)
            RETORNAR TEMPLATES.renderizar("500.html", contexto={"request": requisicao})

    ROTA GET ("/{processo_id}/historico")
    FUNÇÃO web_historico_processo(requisicao: Request, processo_id: Inteiro, sessao_db: Session = INJETAR obter_sessao_banco):
        TENTAR:
            dados_historico = processo_service.consultar_historico_processo(sessao_db, processo_id)
            
            RETORNAR TEMPLATES.renderizar(
                "processos/historico.html",
                contexto={
                    "request": requisicao,
                    "processo": dados_historico.processo,
                    "movimentacoes": dados_historico.historico,
                    "total": dados_historico.total_movimentacoes
                }
            )
        CAPTURAR ExcecaoHttp COMO erro:
            RETORNAR TEMPLATES.renderizar("404.html", contexto={"request": requisicao, "mensagem": erro.detalhe})
    ```

---

### 6. Serviço de Segurança e Controle de Acesso

`/app/services/auth_service.py`
- ação: criar
- descrição: Gerencia a validação de credenciais de usuários e a geração de logs de auditoria (rastreamento do sistema) para operações críticas, em conformidade com o requisito de controle de acesso.
- pseudocódigo:
    ```text
    IMPORTAR pwd_context do passlib.context
    IMPORTAR jwt do jose
    IMPORTAR variaveis_de_ambiente (SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)
    IMPORTAR sqlalchemy.Session
    IMPORTAR Modelos (Usuario, LogAuditoria)

    CONFIGURAR hasher = pwd_context(schemes=["bcrypt"], deprecated="auto")

    FUNÇÃO verificar_senha(senha_plana: String, senha_hasheada: String) RETORNA Booleano:
        RETORNAR hasher.verify(senha_plana, senha_hasheada)

    FUNÇÃO autenticar_usuario(sessao_db: Session, email: String, senha_plana: String):
        usuario = BUSCAR Usuario ONDE email == email
        
        SE usuario É NULO:
            RETORNAR Falso
            
        SE NÃO verificar_senha(senha_plana, usuario.senha_hash):
            RETORNAR Falso
            
        SE usuario.ativo == Falso:
            LEVANTAR ExcecaoHttp(403, "Usuário inativo")
            
        RETORNAR usuario

    FUNÇÃO registrar_log_auditoria(sessao_db: Session, usuario_id: Inteiro, acao: String, recurso: String, detalhes: String):
        NOVO_LOG = LogAuditoria(
            usuario_id = usuario_id,
            acao_realizada = acao,
            recurso_afetado = recurso,
            detalhes = detalhes,
            data_hora = DataHoraAtual
        )
        sessao_db.adicionar(NOVO_LOG)
        sessao_db.confirmar_transacao()
    ```

---

### 7. Infraestrutura de Contêineres (Docker)

`/Dockerfile`
- ação: criar
- descrição: Define a receita para a construção da imagem da aplicação, utilizando uma imagem oficial enxuta do Python. O arquivo expõe a porta necessária para o FastAPI e define o comando de inicialização do servidor Uvicorn.
- pseudocódigo:
    ```dockerfile
    # Utilizar imagem base oficial do Python (versão slim para menor tamanho)
    DE python:3.10-slim

    # Definir o diretório de trabalho dentro do contêiner
    DIRETORIO_TRABALHO /app

    # Copiar arquivo de dependências para o contêiner
    COPIAR requirements.txt .

    # Atualizar pip e instalar dependências sem usar cache para reduzir tamanho da imagem
    EXECUTAR pip install --no-cache-dir --upgrade pip
    EXECUTAR pip install --no-cache-dir -r requirements.txt

    # Copiar todo o código fonte e a estrutura de diretórios para o contêiner
    COPIAR . .

    # Expor a porta 8000 para acesso externo
    EXPOR 8000

    # Comando para iniciar o servidor FastAPI via Uvicorn no modo host global
    COMANDO ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```

`/docker-compose.yml`
- ação: criar
- descrição: Orquestra a execução da aplicação, mapeando a porta externa para a porta do contêiner e estabelecendo um volume persistente para que o banco de dados SQLite não seja perdido quando o contêiner for reiniciado ou destruído.
- pseudocódigo:
    ```yaml
    VERSAO: '3.8'

    SERVICOS:
      web:
        CONSTRUCAO: .
        NOME_CONTEINER: sistema_processos_web
        PORTAS:
          - "8000:8000"
        VOLUMES:
          - ./data:/app/data
        ARQUIVO_ENV:
          - .env
        REINICIAR: always
    ```

---

### 8. Interface de Usuário (Templates SSR - Jinja2 + Bootstrap 5)

`/app/templates/base.html`
- ação: criar
- descrição: Define o esqueleto HTML principal da aplicação utilizando Jinja2 e o framework Bootstrap 5 via CDN. Este arquivo contém a barra de navegação (navbar), a estrutura de grid responsiva e os blocos de conteúdo que serão sobrescritos pelas páginas filhas.
- pseudocódigo:
    ```html
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        DEFINIR metadados e charset (UTF-8)
        IMPORTAR CSS do Bootstrap 5 (CDN)
        IMPORTAR CSS customizado (/static/css/style.css)
        DEFINIR Título Dinâmico: {{ titulo_pagina | default('Gestão de Processos') }}
    </head>
    <body>
        INICIAR NAVBAR (Bootstrap)
            - Link para Dashboard (/processos)
            - Link para Nova Retirada (/processos/retirada)
            - Link para Nova Devolução (/processos/devolucao)
            - Link para Relatórios (/relatorios)
        FIM NAVBAR

        INICIAR CONTAINER_PRINCIPAL (Bootstrap container)
            INICIAR BLOCO DE MENSAGENS_ALERTA (Jinja2 for loop iterando sobre mensagens flash)
                - Renderizar alertas de Sucesso/Erro
            FIM BLOCO

            INICIAR BLOCO_CONTEUDO (Jinja2 block content)
                FIM BLOCO_CONTEUDO
        FIM CONTAINER_PRINCIPAL

        IMPORTAR JS do Bootstrap 5 (Bundle via CDN)
    </body>
    </html>
    ```

`/app/templates/processos/dashboard.html`
- ação: criar
- descrição: Estende o template base para exibir a lista principal de processos. Contém uma tabela estruturada em Bootstrap 5 que itera sobre a lista de processos fornecida pelo backend, além de exibir botões de ação condicionados ao status de cada processo.
- pseudocódigo:
    ```html
    ESTENDER "base.html"

    INICIAR BLOCO_CONTEUDO
        CRIAR CABEÇALHO_PAGINA "Controle de Processos Físicos"
        CRIAR BARRA_DE_BUSCA (Formulário GET para "/processos")
            - Input: Termo de busca (Nome, CPF/CNPJ ou Contrato)
            - Select: Status (Todos, Disponível, Em Posse, Pendente, Liquidado, Arquivado)
            - Botão: "Filtrar"
        
        INICIAR TABELA (Bootstrap table-striped table-hover)
            INICIAR CABEÇALHO_TABELA
                - Colunas: Contrato, Cliente, CPF/CNPJ, Status, Setor, Ações
            FIM CABEÇALHO_TABELA
            
            INICIAR CORPO_TABELA
                PARA CADA processo EM lista_processos:
                    INICIAR LINHA
                        COLUNA: processo.numero_contrato
                        COLUNA: processo.nome_cliente
                        COLUNA: processo.cpf_cnpj
                        COLUNA: CRIAR BADGE_BOOTSTRAP(processo.status)
                        COLUNA: processo.setor_responsavel
                        COLUNA (Ações):
                            SE processo.status == "Disponível":
                                - Botão Link: "Retirar" (Aponta para "/processos/retirar/{processo.id}")
                            SE processo.status == "Em Posse":
                                - Botão Link: "Devolver" (Aponta para "/processos/devolver/{processo.id}")
                            - Botão Link: "Histórico" (Aponta para "/processos/historico/{processo.id}")
                    FIM LINHA
                SE lista_processos VAZIA:
                    CRIAR LINHA "Nenhum processo encontrado."
            FIM CORPO_TABELA
        FIM TABELA
    FIM BLOCO_CONTEUDO
    ```