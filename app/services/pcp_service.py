from psycopg.rows import dict_row
from app.extensions import get_db

def resumo_dashboard(filtros):
    where = []
    params = []

    if filtros.get("data_inicial") and filtros.get("data_final"):
        where.append("data BETWEEN %s AND %s")
        params.extend([filtros["data_inicial"], filtros["data_final"]])

    if filtros.get("turno"):
        where.append("turno = %s")
        params.append(filtros["turno"])

    if filtros.get("filial"):
        where.append("filial = %s")
        params.append(filtros["filial"])

    where_sql = " AND ".join(where)
    if where_sql:
        where_sql = "WHERE " + where_sql

    query = f"""
        SELECT
            linha,
            setor,
            filial,
            SUM(hc_padrao) AS hc_planejado,
            SUM(hc_real)   AS hc_real
        FROM lancamentos
        {where_sql}
        GROUP BY linha, setor, filial
    """

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

    dados = []
    total_p = total_r = 0

    for r in rows:
        absenteismo = 0
        if r["hc_planejado"] > 0:
            absenteismo = round(
                (r["hc_planejado"] - r["hc_real"]) / r["hc_planejado"] * 100, 2
            )

        status = "OK" if r["hc_real"] >= r["hc_planejado"] else "CRÍTICO"

        dados.append({
            "nome": r["linha"],
            "setor": r["setor"],
            "filial": r["filial"],
            "hc_planejado": r["hc_planejado"],
            "hc_real": r["hc_real"],
            "absenteismo": absenteismo,
            "status": status
        })

        total_p += r["hc_planejado"]
        total_r += r["hc_real"]

    ranking_linhas = sorted(dados, key=lambda x: x["absenteismo"], reverse=True)

    # Ranking por SETOR
    ranking_setor = {}
    for d in dados:
        ranking_setor.setdefault(d["setor"], []).append(d)

    ranking_setor = sorted(
        [{
            "nome": setor,
            "absenteismo": round(
                sum(i["absenteismo"] for i in itens) / len(itens), 2
            )
        } for setor, itens in ranking_setor.items()],
        key=lambda x: x["absenteismo"],
        reverse=True
    )

    # Ranking por FILIAL
    ranking_filial = {}
    for d in dados:
        ranking_filial.setdefault(d["filial"], []).append(d)

    ranking_filial = sorted(
        [{
            "nome": filial,
            "absenteismo": round(
                sum(i["absenteismo"] for i in itens) / len(itens), 2
            )
        } for filial, itens in ranking_filial.items()],
        key=lambda x: x["absenteismo"],
        reverse=True
    )

    abs_total = 0
    if total_p > 0:
        abs_total = round((total_p - total_r) / total_p * 100, 2)

    return {
        "dados": dados,
        "ranking_linhas": ranking_linhas[:5],
        "ranking_setor": ranking_setor,
        "ranking_filial": ranking_filial,
        "kpis": {
            "hc_planejado": total_p,
            "hc_real": total_r,
            "absenteismo": abs_total,
            "linhas": len(dados)
        }
    }

def ranking_cargos(filtros):
    where = []
    params = []

    if filtros.get("data_inicial") and filtros.get("data_final"):
        where.append("l.data BETWEEN %s AND %s")
        params += [filtros["data_inicial"], filtros["data_final"]]

    where_sql = " AND ".join(where)
    if where_sql:
        where_sql = "WHERE " + where_sql

    query = f"""
        SELECT
            c.nome,
            SUM(lc.quantidade) AS total
        FROM lancamentos_cargos lc
        JOIN cargos c ON c.id = lc.cargo_id
        JOIN lancamentos l ON l.id = lc.lancamento_id
        {where_sql}
        GROUP BY c.nome
        ORDER BY total DESC
    """

    with get_db() as conn:
        # <-- use DictCursor aqui
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, params)
            return cur.fetchall()
