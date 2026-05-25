# Relatório de Inspeção de Cibersegurança: sistemaDocUAB

## 1. Resumo Executivo

Esta inspeção detalhada do sistemaDocUAB revelou várias vulnerabilidades que comprometem a integridade, confidencialidade e disponibilidade do sistema. A falha mais crítica é a presença de chaves secretas padrão e senhas administrativas "hardcoded", o que permitiria a um atacante comprometer totalmente a autenticação do sistema. Além disso, a ausência de proteções fundamentais como CSRF e cabeçalhos de segurança HTTP expõe os usuários a ataques comuns da Web.

### Contagem de Achados por Severidade
- **Crítica**: 1
- **Alta**: 3
- **Média**: 4
- **Baixa**: 2
- **Total**: 10

### Top 5 Ações Mais Urgentes
1. **Alterar a `SECRET_KEY` padrão**: Substituir o valor "your-secret-key" por uma chave forte gerada aleatoriamente e armazenada apenas em variáveis de ambiente.
2. **Implementar Proteção CSRF**: Adicionar middleware de proteção contra Cross-Site Request Forgery em todos os formulários POST.
3. **Corrigir Configuração do Docker**: Alterar o `Dockerfile` para que a aplicação não seja executada como usuário `root`.
4. **Reforçar a Segurança de Cookies**: Adicionar os atributos `Secure`, `HttpOnly` e `SameSite` aos cookies de autenticação.
5. **Sanitização de Erros**: Remover a exposição de exceções brutas (`str(e)`) para os usuários finais em templates.

---

## 2. Vulnerabilidades Detalhadas

### V01: Uso de Chave Secreta Padrão (Hardcoded)
- **Localização**: `app/services/auth_service.py`, Linha 16
- **Descrição**: O sistema utiliza uma `SECRET_KEY` padrão ("your-secret-key") definida no código. Isso permite que atacantes forjem tokens JWT, permitindo a personificação de qualquer usuário, incluindo administradores.
- **Evidência**:
  ```python
  SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
  ```
- **Impacto**: Comprometimento total da autenticação e autorização (Quebra de Confidencialidade e Integridade).
- **Severidade**: **Crítica**
- **Recomendação**: Remover o valor padrão e garantir que a aplicação falhe ao iniciar se `SECRET_KEY` não estiver definida nas variáveis de ambiente.
- **Referências**: CWE-798 (Use of Hard-coded Credentials), OWASP A02:2021, A04:2021.

### V02: Ausência de Proteção contra CSRF
- **Localização**: `app/routers/views.py`, `app/routers/auth.py` e todos os templates de formulário.
- **Descrição**: O sistema utiliza autenticação baseada em cookies sem implementar tokens CSRF. Um atacante pode induzir um usuário autenticado a realizar ações indesejadas (como criar usuários ou alterar processos).
- **Evidência**: O `app/main.py` não possui middleware de CSRF e os formulários em `app/templates/` não incluem tokens de validação.
- **Impacto**: Execução de ações não autorizadas em nome do usuário logado.
- **Severidade**: **Alta**
- **Recomendação**: Utilizar uma biblioteca como `fastapi-csrf` ou implementar a validação de tokens CSRF em todas as rotas de mutação (POST, PUT, DELETE).
- **Referências**: CWE-352 (Cross-Site Request Forgery), OWASP A01:2021.

### V03: Execução de Contêiner como Root
- **Localização**: `Dockerfile`
- **Descrição**: A aplicação no contêiner Docker é executada como o usuário `root`. Se a aplicação for comprometida, o atacante terá privilégios totais dentro do contêiner.
- **Evidência**: O `Dockerfile` não define um usuário não privilegiado (`USER`).
- **Impacto**: Escalada de privilégios e maior impacto em caso de exploração de outras vulnerabilidades.
- **Severidade**: **Alta**
- **Recomendação**: Adicionar a criação de um usuário de sistema e o comando `USER` no Dockerfile.
  ```dockerfile
  RUN addgroup --system appuser && adduser --system --group appuser
  USER appuser
  ```
- **Referências**: OWASP A02:2021 (Security Misconfiguration).

### V04: Senha Administrativa Padrão em Script de Seed
- **Localização**: `seed_admin.py`, Linha 14
- **Descrição**: O script de inicialização define uma senha padrão fraca ("admin123") para o administrador.
- **Evidência**:
  ```python
  senha_hash=get_password_hash("admin123"),
  ```
- **Impacto**: Acesso não autorizado se o script for executado em produção sem alteração imediata da senha.
- **Severidade**: **Média**
- **Recomendação**: Utilizar variáveis de ambiente para definir a senha inicial ou forçar a alteração no primeiro login.
- **Referências**: CWE-259 (Use of Hard-coded Password), OWASP A07:2021.

### V05: Configuração de Cookie Insegura
- **Localização**: `app/routers/auth.py`, Linha 42
- **Descrição**: O cookie `access_token` não possui as flags `Secure` e `SameSite`. A ausência de `Secure` permite a interceptação do token em conexões não criptografadas (HTTP).
- **Evidência**:
  ```python
  response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
  ```
- **Impacto**: Sequestro de sessão (Session Hijacking).
- **Severidade**: **Média**
- **Recomendação**: Configurar `secure=True`, `samesite='lax'` e definir um tempo de expiração (`max_age`).
- **Referências**: CWE-614 (Sensitive Cookie in HTTPS Session Without 'Secure' Attribute), OWASP A07:2021.

### V06: Ausência de Cabeçalhos de Segurança HTTP
- **Localização**: `app/main.py`
- **Descrição**: A aplicação não implementa cabeçalhos de segurança básicos como `Content-Security-Policy`, `X-Frame-Options` e `Strict-Transport-Security`.
- **Evidência**: O objeto `FastAPI` é instanciado sem middlewares de segurança.
- **Impacto**: Vulnerabilidade a ataques de Clickjacking, XSS e downgrade de protocolo.
- **Severidade**: **Média**
- **Recomendação**: Implementar middleware para adicionar cabeçalhos de segurança recomendados.
- **Referências**: OWASP A05:2021.

### V07: Falha no Registro de Auditoria (Logging)
- **Localização**: Diversas rotas em `app/routers/`
- **Descrição**: Embora exista uma função `registrar_log_auditoria` em `auth_service.py`, ela não é chamada durante ações críticas como criação de usuários ou movimentação de processos.
- **Evidência**: Falta de chamadas para `auth_service.registrar_log_auditoria` nas rotas POST em `views.py`.
- **Impacto**: Dificuldade em investigar incidentes e detectar atividades maliciosas (Não repúdio).
- **Severidade**: **Média**
- **Recomendação**: Integrar o registro de logs em todas as operações de escrita no banco de dados.
- **Referências**: OWASP A09:2021 (Security Logging and Alerting Failures).

### V08: Controle de Acesso Baseado em Lógica de Função (Incompleto)
- **Localização**: `app/routers/usuarios.py`
- **Descrição**: As verificações de privilégios (`is_admin`) são feitas manualmente dentro das funções, em vez de serem dependências de rota. Se um desenvolvedor esquecer a chamada manual, a rota fica exposta.
- **Evidência**:
  ```python
  auth_service.is_admin(current_user) # Chamada manual dentro do corpo da função
  ```
- **Impacto**: Acesso não autorizado a funções administrativas.
- **Severidade**: **Média**
- **Recomendação**: Utilizar dependências do FastAPI para garantir o controle de acesso antes da execução da lógica da rota.
- **Referências**: OWASP A01:2021 (Broken Access Control).

### V09: Exposição de Informações Sensíveis em Mensagens de Erro
- **Localização**: `app/routers/views.py` e `app/routers/usuarios.py`
- **Descrição**: O sistema captura exceções e as envia diretamente para o frontend, o que pode revelar detalhes da estrutura do banco de dados ou caminhos de arquivos.
- **Evidência**: `context={"erro": str(e)}` em blocos `except`.
- **Impacto**: Vazamento de informações técnicas que auxiliam no reconhecimento do alvo.
- **Severidade**: **Baixa**
- **Recomendação**: Exibir mensagens genéricas para o usuário e logar os detalhes técnicos apenas no servidor.
- **Referências**: CWE-209 (Generation of Error Message Containing Sensitive Information), OWASP A10:2021.

### V10: Ausência de Subresource Integrity (SRI) para CDNs
- **Localização**: `app/templates/base.html`
- **Descrição**: Links para bibliotecas externas (Bootstrap, Chart.js) não utilizam hashes SRI.
- **Evidência**:
  ```html
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  ```
- **Impacto**: Se a CDN for comprometida, um atacante pode injetar scripts maliciosos no navegador dos usuários.
- **Severidade**: **Baixa**
- **Recomendação**: Adicionar os atributos `integrity` e `crossorigin` em todos os links de recursos externos.
- **Referências**: OWASP A03:2021 (Software Supply Chain Failures).
