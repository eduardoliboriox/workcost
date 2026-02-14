from datetime import datetime, time, timedelta


# ===============================
# CONFIGURAÇÕES (FUTURO: BD)
# ===============================

ADICIONAL_NOTURNO_PERCENTUAL = 0.20

CUSTOS_REFEICAO = {
    "lanche": 12.00,
    "almoco": 28.00,
    "jantar": 30.00,
}

CUSTO_TRANSPORTE = {
    "ROTA": 18.00,
    "VEICULO": 25.00,
}


# ===============================
# UTILITÁRIOS
# ===============================

def calcular_horas(inicio_str, termino_str):
    fmt = "%H:%M"

    inicio = datetime.strptime(inicio_str, fmt)
    termino = datetime.strptime(termino_str, fmt)

    if termino <= inicio:
        termino += timedelta(days=1)

    total = termino - inicio
    return total.total_seconds() / 3600


def calcular_horas_noturnas(inicio_str, termino_str):
    fmt = "%H:%M"
    inicio = datetime.strptime(inicio_str, fmt)
    termino = datetime.strptime(termino_str, fmt)

    if termino <= inicio:
        termino += timedelta(days=1)

    noturno_inicio = time(22, 0)
    noturno_fim = time(5, 0)

    horas_noturnas = 0
    atual = inicio

    while atual < termino:
        proximo = min(atual + timedelta(minutes=30), termino)

        if (
            atual.time() >= noturno_inicio
            or atual.time() <= noturno_fim
        ):
            horas_noturnas += (proximo - atual).total_seconds() / 3600

        atual = proximo

    return round(horas_noturnas, 2)


def calcular_refeicoes(turno: str):
    if turno == "1T":
        return CUSTOS_REFEICAO["lanche"] + CUSTOS_REFEICAO["almoco"]
    if turno == "2T":
        return CUSTOS_REFEICAO["lanche"] + CUSTOS_REFEICAO["jantar"]
    if turno == "3T":
        return CUSTOS_REFEICAO["lanche"]
    return 0


def calcular_transporte(tipo: str):
    return CUSTO_TRANSPORTE.get(tipo, 0)


# ===============================
# FUNÇÃO PRINCIPAL
# ===============================

def gerar_provisao(solicitacao, funcionarios):
    resultado = []
    total_geral = 0

    turno = solicitacao["turnos"]

    for f in funcionarios:

        horas = calcular_horas(f["inicio"], f["termino"])
        horas_noturnas = calcular_horas_noturnas(
            f["inicio"], f["termino"]
        )

        custo_refeicao = calcular_refeicoes(turno)
        custo_transporte = calcular_transporte(f["transporte"])

        adicional_noturno = horas_noturnas * ADICIONAL_NOTURNO_PERCENTUAL

        total_funcionario = (
            custo_refeicao
            + custo_transporte
            + adicional_noturno
        )

        total_geral += total_funcionario

        resultado.append({
            "matricula": f["matricula"],
            "nome": f["nome"],
            "horas_total": horas,
            "horas_noturnas": horas_noturnas,
            "custo_refeicao": custo_refeicao,
            "custo_transporte": custo_transporte,
            "adicional_noturno": adicional_noturno,
            "total": round(total_funcionario, 2)
        })

    return {
        "funcionarios": resultado,
        "total_geral": round(total_geral, 2)
    }
