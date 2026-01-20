from app.repositories import lancamentos_repository

def calcular_absenteismo(hc_padrao, hc_real):
    if hc_padrao <= 0:
        return 0
    return round((hc_padrao - hc_real) / hc_padrao * 100, 2)

def criar_lancamento(dados):
    dados = dict(dados)

    cargos = json.loads(dados.pop("cargos"))

    absenteismo = calcular_absenteismo(
        int(dados["hc_padrao"]),
        int(dados["hc_real"])
    )

    dados["absenteismo"] = absenteismo

    lancamentos_repository.inserir_com_cargos(dados, cargos)

    return {"sucesso": True, "absenteismo": absenteismo}


