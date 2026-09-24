import httpx, os

BASE = "http://127.0.0.1:8000"
r = httpx.post(f"{BASE}/login", json={"email": "admin@docuab.com", "senha": "admin123"})
h = {"Authorization": "Bearer " + r.json()["access_token"]}
st = httpx.get(f"{BASE}/api/configuracoes/status", headers=h).json()
sid = [s["id"] for s in st if s["nome"].startswith("Dispon")][0]
c = httpx.post(
    f"{BASE}/api/processos/cadastrar",
    headers=h,
    json={
        "nome_cliente": "Debug",
        "cpf_cnpj": "333.333.333-" + os.urandom(2).hex(),
        "numero_contrato": "DBG-" + os.urandom(3).hex(),
        "tipo_processo": "Cadastro",
        "setor_responsavel": "Administrativo",
        "status_id": sid,
    },
)
print("cadastrar:", c.status_code, c.text[:200])
pid = c.json()["id"]
ret = httpx.post(
    f"{BASE}/api/processos/movimentar/retirada",
    params={"processo_id": pid, "setor_destino": "Fiscalizacao"},
    headers=h,
)
print("retirada:", ret.status_code)
print("retirada body:", ret.text[:600])
