import json
from app.repositories import lancamentos_repository

def calcular_absenteismo(hc_padrao, hc_real):
    if hc_padrao <= 0:
        return 0
    return round((hc_padrao - hc_real) / hc_padrao * 100, 2)

def criar_lancamento(dados):
    dados = dict(dados)

    cargos = json.loads(dados.pop("cargos", "[]"))

    hc_padrao = int(dados["hc_padrao"])

    # 🔥 SOMA DAS FALTAS
    total_faltas = sum(c["quantidade"] for c in cargos)

    # 🔥 HC REAL AUTOMÁTICO
    hc_real = hc_padrao - total_faltas
    if hc_real < 0:
        hc_real = 0

    dados["hc_real"] = hc_real

    absenteismo = calcular_absenteismo(hc_padrao, hc_real)
    dados["absenteismo"] = absenteismo

    lancamentos_repository.inserir_com_cargos(dados, cargos)

    return {
        "sucesso": True,
        "hc_real": hc_real,
        "absenteismo": absenteismo
    }
