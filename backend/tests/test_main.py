import pytest
import httpx
import os

# Configurações para os testes
# 127.0.0.1 evita que 'localhost' resolva para IPv6/outros serviços na porta 8000
BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api"

@pytest.fixture
def admin_token():
    # Assume que o admin padrão existe (admin@docuab.com / admin123)
    response = httpx.post(f"{BASE_URL}/login", json={"email": "admin@docuab.com", "senha": "admin123"})
    assert response.status_code == 200
    return response.json()["access_token"]

def test_login_invalido():
    response = httpx.post(f"{BASE_URL}/login", json={"email": "errado@teste.com", "senha": "123"})
    assert response.status_code == 401

def test_listar_processos_sem_token():
    response = httpx.get(f"{API_URL}/processos/")
    assert response.status_code == 401

def test_crud_processo_admin(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Buscar status ID para "Disponível"
    status_res = httpx.get(f"{API_URL}/configuracoes/status", headers=headers)
    status_id = [s["id"] for s in status_res.json() if s["nome"] == "Disponível"][0]

    # 2. Cadastrar
    contrato = f"TEST-{os.urandom(4).hex()}"
    payload = {
        "nome_cliente": "Cliente Teste Pytest",
        "cpf_cnpj": f"000.000.000-{os.urandom(2).hex()}",
        "numero_contrato": contrato,
        "tipo_processo": "Cadastro",
        "setor_responsavel": "Administrativo",
        "status_id": status_id,
        "observacao": "Teste automatizado"
    }
    
    create_res = httpx.post(f"{API_URL}/processos/cadastrar", json=payload, headers=headers)
    assert create_res.status_code == 201
    processo_id = create_res.json()["id"]

    # 3. Listar e verificar se está lá
    list_res = httpx.get(f"{API_URL}/processos/", headers=headers)
    assert any(p["id"] == processo_id for p in list_res.json()["processos"])

def test_fluxo_movimentacao(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Criar processo disponível
    status_res = httpx.get(f"{API_URL}/configuracoes/status", headers=headers)
    status_disp = [s for s in status_res.json() if s["nome"] == "Disponível"][0]
    
    contrato = f"MOV-{os.urandom(4).hex()}"
    payload = {
        "nome_cliente": "Teste Movimentacao",
        "cpf_cnpj": f"111.111.111-{os.urandom(2).hex()}",
        "numero_contrato": contrato,
        "tipo_processo": "Cadastro",
        "setor_responsavel": "Administrativo",
        "status_id": status_disp["id"]
    }
    proc = httpx.post(f"{API_URL}/processos/cadastrar", json=payload, headers=headers).json()
    
    # 2. Retirar
    ret_res = httpx.post(f"{API_URL}/processos/movimentar/retirada", params={
        "processo_id": proc["id"],
        "setor_destino": "Juridico",
        "observacoes": "Saída via teste"
    }, headers=headers)
    assert ret_res.status_code == 200
    
    # 3. Verificar se status mudou para "Em Posse"
    check_res = httpx.get(f"{API_URL}/processos/", headers=headers)
    updated_proc = [p for p in check_res.json()["processos"] if p["id"] == proc["id"]][0]
    assert updated_proc["status"]["nome"] == "Em Posse"

def test_acesso_setor_restrito(admin_token):
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Criar um usuário para o setor Juridico
    user_payload = {
        "nome": "Usuário Juridico Teste",
        "email": f"teste_juridico_{os.urandom(2).hex()}@teste.com",
        "senha": "password123",
        "cargo": "usuario",
        "setor": "Juridico"
    }
    httpx.post(f"{API_URL}/usuarios/cadastrar", json=user_payload, headers=headers_admin)
    
    # 2. Logar com esse usuário
    login_res = httpx.post(f"{BASE_URL}/login", json={"email": user_payload["email"], "senha": "password123"})
    user_token = login_res.json()["access_token"]
    headers_user = {"Authorization": f"Bearer {user_token}"}
    
    # 3. Listar processos (deve ver apenas Juridico)
    list_res = httpx.get(f"{API_URL}/processos/", headers=headers_user)
    for p in list_res.json()["processos"]:
        assert p["setor_responsavel"] == "Juridico"


def _criar_usuario_setor(setor, admin_token):
    """Cadastra um usuário comum no setor informado e devolve os headers de auth."""
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    user_payload = {
        "nome": f"Usuário {setor} Teste",
        "email": f"teste_{setor.lower()}_{os.urandom(3).hex()}@teste.com",
        "senha": "password123",
        "cargo": "usuario",
        "setor": setor,
    }
    create_res = httpx.post(f"{API_URL}/usuarios/cadastrar", json=user_payload, headers=headers_admin)
    assert create_res.status_code == 201

    login_res = httpx.post(
        f"{BASE_URL}/login",
        json={"email": user_payload["email"], "senha": "password123"},
    )
    assert login_res.status_code == 200
    return {"Authorization": f"Bearer {login_res.json()['access_token']}"}


def _criar_processo_admin(admin_token, setor="Administrativo"):
    """Cadastra um processo 'Disponível' no setor informado e devolve o id."""
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    status_res = httpx.get(f"{API_URL}/configuracoes/status", headers=headers_admin)
    status_id = [s["id"] for s in status_res.json() if s["nome"] == "Disponível"][0]

    payload = {
        "nome_cliente": "Cliente Restricao Teste",
        "cpf_cnpj": f"222.222.222-{os.urandom(2).hex()}",
        "numero_contrato": f"REST-{os.urandom(4).hex()}",
        "tipo_processo": "Cadastro",
        "setor_responsavel": setor,
        "status_id": status_id,
    }
    create_res = httpx.post(f"{API_URL}/processos/cadastrar", json=payload, headers=headers_admin)
    assert create_res.status_code == 201
    return create_res.json()["id"]


def test_historico_setor_restrito(admin_token):
    processo_id = _criar_processo_admin(admin_token, setor="Administrativo")
    headers_user = _criar_usuario_setor("Juridico", admin_token)

    res = httpx.get(f"{API_URL}/processos/{processo_id}/historico", headers=headers_user)
    assert res.status_code == 404


def test_retirada_setor_restrito(admin_token):
    processo_id = _criar_processo_admin(admin_token, setor="Administrativo")
    headers_user = _criar_usuario_setor("Juridico", admin_token)

    res = httpx.post(
        f"{API_URL}/processos/movimentar/retirada",
        params={"processo_id": processo_id, "setor_destino": "Juridico"},
        headers=headers_user,
    )
    assert res.status_code == 404

    # O processo não pode ter sido movimentado: continua "Disponível"
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    list_res = httpx.get(f"{API_URL}/processos/", headers=headers_admin)
    proc = [p for p in list_res.json()["processos"] if p["id"] == processo_id][0]
    assert proc["status"]["nome"] == "Disponível"


def test_devolucao_setor_restrito(admin_token):
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    processo_id = _criar_processo_admin(admin_token, setor="Administrativo")

    # Admin retira para um terceiro setor, gerando movimentação ativa
    ret_res = httpx.post(
        f"{API_URL}/processos/movimentar/retirada",
        params={"processo_id": processo_id, "setor_destino": "Fiscalizacao"},
        headers=headers_admin,
    )
    assert ret_res.status_code == 200
    mov_id = ret_res.json()["id"]

    # Usuário de um setor sem relação com o processo não pode devolver
    headers_user = _criar_usuario_setor("Juridico", admin_token)
    res = httpx.post(
        f"{API_URL}/processos/movimentar/devolucao",
        json={"movimentacao_id": mov_id, "novo_status_processo": "Disponível"},
        headers=headers_user,
    )
    assert res.status_code == 404
