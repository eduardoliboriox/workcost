from datetime import datetime, time, timedelta, date
from decimal import Decimal, ROUND_HALF_UP

from app.repositories.employees_repository import (
    get_clt_remuneracao_mensal_by_matricula
)

# ===============================
# CONFIGURAÇÕES (FUTURO: BD)
# ===============================

ADICIONAL_NOTURNO_PERCENTUAL = Decimal("0.20")

JORNADA_MENSAL_HORAS_PADRAO = Decimal("220")

CUSTOS_REFEICAO = {
    "lanche": Decimal("12.00"),
    "almoco": Decimal("28.00"),
    "jantar": Decimal("30.00"),
}

CUSTO_TRANSPORTE = {
    "ROTA": Decimal("18.00"),
    "VEICULO": Decimal("25.00"),
}


# ===============================
# UTILITÁRIOS
# ===============================

def _money(v: Decimal) -> Decimal:
    return (v or Decimal("0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def _to_datetime(valor):
    """
    Converte:
    - string 'HH:MM'
    - datetime.time
    para datetime seguro.
    """
    if isinstance(valor, time):
        return datetime.combine(datetime.today(), valor)

    if isinstance(valor, str):
        return datetime.strptime(valor, "%H:%M")

    raise TypeError(f"Formato de hora não suportado: {type(valor)}")

def calcular_horas(inicio_valor, termino_valor):

    inicio = _to_datetime(inicio_valor)
    termino = _to_datetime(termino_valor)

    if termino <= inicio:
        termino += timedelta(days=1)

    total = termino - inicio
    return round(total.total_seconds() / 3600, 2)

def calcular_horas_noturnas(inicio_valor, termino_valor):

    inicio = _to_datetime(inicio_valor)
    termino = _to_datetime(termino_valor)

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
    return Decimal("0")

def calcular_transporte(tipo: str):
    return CUSTO_TRANSPORTE.get(tipo, Decimal("0"))

def _parse_date_iso(value) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except Exception:
        return None

# ===============================
# FERIADOS (BR) p/ DSR
# - objetivo: automatizar o reflexo 854 (DSR) com base no mês
# - fator: (dias_descanso / dias_uteis) * adicional_noturno
# ===============================

def _easter_sunday(year: int) -> date:
    # Algoritmo de Meeus/Jones/Butcher
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)

def _br_holidays(year: int) -> set[date]:
    """
    Feriados nacionais mais comuns + móveis (baseados na Páscoa).
    (Suficiente para automatizar DSR no custo mensal com boa fidelidade)
    """
    easter = _easter_sunday(year)
    good_friday = easter - timedelta(days=2)
    carnaval_monday = easter - timedelta(days=48)
    carnaval_tuesday = easter - timedelta(days=47)
    corpus_christi = easter + timedelta(days=60)

    fixed = {
        date(year, 1, 1),   # Confraternização Universal
        date(year, 4, 21),  # Tiradentes
        date(year, 5, 1),   # Dia do Trabalho
        date(year, 9, 7),   # Independência
        date(year, 10, 12), # Nossa Senhora Aparecida
        date(year, 11, 2),  # Finados
        date(year, 11, 15), # Proclamação da República
        date(year, 12, 25), # Natal
    }

    movable = {good_friday, carnaval_monday, carnaval_tuesday, corpus_christi}
    return fixed | movable

def _month_days(year: int, month: int) -> int:
    if month == 2:
        leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
        return 29 if leap else 28
    if month in (1,3,5,7,8,10,12):
        return 31
    return 30

def _dsr_ratio_for_month(base_date: date) -> Decimal:
    """
    DSR variável (reflexo) aproximado:
    ratio = dias_descanso / dias_uteis

    dias_descanso:
    - domingos do mês
    - feriados nacionais que caem em dia útil (seg-sex) + feriado em sábado (depende da empresa)
      aqui consideramos feriado (seg-sáb) como descanso e ignoramos se cair no domingo (pra não duplicar)
    """
    year, month = base_date.year, base_date.month
    total_days = _month_days(year, month)
    holidays = {d for d in _br_holidays(year) if d.month == month}

    sundays = 0
    holidays_count = 0

    for day in range(1, total_days + 1):
        d = date(year, month, day)
        if d.weekday() == 6:  
            sundays += 1

    for h in holidays:
        if h.weekday() != 6:
            holidays_count += 1

    dias_descanso = sundays + holidays_count
    dias_uteis = total_days - sundays - holidays_count

    if dias_uteis <= 0:
        return Decimal("0")

    return (Decimal(dias_descanso) / Decimal(dias_uteis))

def _valor_hora_clt(remuneracao_mensal) -> Decimal | None:
    if remuneracao_mensal is None:
        return None
    try:
        rm = Decimal(str(remuneracao_mensal))
    except Exception:
        return None
    if rm <= 0:
        return None
    return (rm / JORNADA_MENSAL_HORAS_PADRAO)

# ===============================
# FUNÇÃO PRINCIPAL
# ===============================

def gerar_provisao(solicitacao, funcionarios):
    """
    Agora inclui:
    - adicional_noturno_valor (real, baseado em salário CLT / 220)
    - reflexo_adic_noturno_dsr (854) com base no mês (domingos + feriados nacionais)
    """
    resultado = []
    total_geral = Decimal("0")

    turno = solicitacao["turnos"]

    base_date = (
        _parse_date_iso(solicitacao.get("data_execucao"))
        or _parse_date_iso(solicitacao.get("data"))
        or date.today()
    )
    dsr_ratio = _dsr_ratio_for_month(base_date)

    for f in funcionarios:

        horas = Decimal(str(calcular_horas(f["inicio"], f["termino"])))
        horas_noturnas = Decimal(str(calcular_horas_noturnas(
            f["inicio"], f["termino"]
        )))

        custo_refeicao = calcular_refeicoes(turno)
        custo_transporte = calcular_transporte(f["transporte"])

        # =========================
        # CÁLCULO REAL DO NOTURNO (CLT)
        # =========================
        remuneracao_mensal = get_clt_remuneracao_mensal_by_matricula(f.get("matricula"))
        valor_hora = _valor_hora_clt(remuneracao_mensal)

        if valor_hora is None:
            adicional_noturno_valor = Decimal("0")
            reflexo_dsr = Decimal("0")
            salario_ok = False
        else:
            adicional_noturno_valor = (valor_hora * horas_noturnas * ADICIONAL_NOTURNO_PERCENTUAL)
            reflexo_dsr = (adicional_noturno_valor * dsr_ratio)
            salario_ok = True

        adicional_noturno_valor = _money(adicional_noturno_valor)
        reflexo_dsr = _money(reflexo_dsr)

        total_funcionario = (
            custo_refeicao
            + custo_transporte
            + adicional_noturno_valor
            + reflexo_dsr
        )

        total_geral += total_funcionario

        resultado.append({
            "matricula": f["matricula"],
            "nome": f["nome"],
            "horas_total": float(horas),
            "horas_noturnas": float(horas_noturnas),
            "custo_refeicao": float(_money(custo_refeicao)),
            "custo_transporte": float(_money(custo_transporte)),

            "adicional_noturno_valor": float(adicional_noturno_valor),
            "reflexo_adic_noturno_dsr": float(reflexo_dsr),

            "adicional_noturno": float(adicional_noturno_valor),

            "salario_clt_informado": salario_ok,
            "total": float(_money(total_funcionario)),
        })

    return {
        "funcionarios": resultado,
        "total_geral": float(_money(total_geral)),
        "meta": {
            "base_month": base_date.strftime("%Y-%m"),
            "dsr_ratio": float(_money(dsr_ratio)),
        }
    }
