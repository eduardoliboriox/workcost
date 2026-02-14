# app/services/relatorios_service.py
from app.extensions import get_db
from psycopg.rows import dict_row
from datetime import date, timedelta
from app.services.provisao_service import gerar_provisao
from app.repositories.solicitacoes_repository import (
    buscar_solicitacao_por_id,
    listar_funcionarios_por_solicitacao
)

def _formatar_data_br(d: date) -> str:
    """Formata data para padrão brasileiro DD-MM-YYYY"""
    return d.strftime("%d-%m-%Y")

def gerar_relatorio(setor, tipo):
    hoje = date.today()

    if not setor:
        setor = None

    if tipo == "SEMANAL":
        data_inicial = hoje - timedelta(days=7)
    elif tipo == "MENSAL":
        data_inicial = hoje.replace(day=1)
    else:
        data_inicial = hoje.replace(month=1, day=1)

    # ===============================
    # Ranking de linhas por faltas
    # ===============================
    base_query = """
        SELECT
            l.linha,
            COALESCE(SUM(lc.quantidade), 0) AS total_faltas
        FROM lancamentos l
        JOIN lancamentos_cargos lc ON lc.lancamento_id = l.id
        WHERE lc.tipo = 'FALTA'
          AND l.data BETWEEN %s AND %s
    """

    if setor:
        query = base_query + """
          AND l.setor = %s
          GROUP BY l.linha
          ORDER BY total_faltas DESC
          LIMIT 10
        """
        params = (data_inicial, hoje, setor)
    else:
        query = base_query + """
          GROUP BY l.linha
          ORDER BY total_faltas DESC
          LIMIT 10
        """
        params = (data_inicial, hoje)

    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, params)
            linhas = cur.fetchall() or []

    # ==========================================
    # Cargo crítico GLOBAL (visão executiva)
    # ==========================================
    cargo_query = """
        SELECT
            c.nome,
            SUM(lc.quantidade) AS total
        FROM lancamentos_cargos lc
        JOIN cargos c ON c.id = lc.cargo_id
        JOIN lancamentos l ON l.id = lc.lancamento_id
        WHERE lc.tipo = 'FALTA'
          AND l.data BETWEEN %s AND %s
        GROUP BY c.nome
        ORDER BY total DESC
        LIMIT 1
    """

    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(cargo_query, (data_inicial, hoje))
            cargo_critico_global = cur.fetchone()

    # =====================================================
    # Cargo crítico POR LINHA + percentual dentro da linha
    # =====================================================
    linha_cargo_query = """
        WITH total_linha AS (
            SELECT
                l.linha,
                SUM(lc.quantidade) AS total_linha
            FROM lancamentos l
            JOIN lancamentos_cargos lc ON lc.lancamento_id = l.id
            WHERE lc.tipo = 'FALTA'
              AND l.data BETWEEN %s AND %s
              AND l.linha = %s
            GROUP BY l.linha
        )
        SELECT
            c.nome AS cargo,
            SUM(lc.quantidade) AS total,
            ROUND(
                SUM(lc.quantidade) * 100.0 / tl.total_linha,
                2
            ) AS percentual_linha
        FROM lancamentos_cargos lc
        JOIN cargos c ON c.id = lc.cargo_id
        JOIN lancamentos l ON l.id = lc.lancamento_id
        JOIN total_linha tl ON tl.linha = l.linha
        WHERE lc.tipo = 'FALTA'
          AND l.data BETWEEN %s AND %s
          AND l.linha = %s
        GROUP BY c.nome, tl.total_linha
        ORDER BY total DESC
        LIMIT 1
    """

    # Enriquecendo cada linha com análise de cargo
    for linha in linhas:
        with get_db() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    linha_cargo_query,
                    (
                        data_inicial,
                        hoje,
                        linha["linha"],
                        data_inicial,
                        hoje,
                        linha["linha"],
                    ),
                )
                linha["cargo_critico"] = cur.fetchone()

    return {
        "periodo": f"{_formatar_data_br(data_inicial)} até {_formatar_data_br(hoje)}",
        "linhas": linhas,
        "cargo_critico": cargo_critico_global,
    }


def gerar_provisao_gastos_extra(solicitacao_id: int):

    solicitacao = buscar_solicitacao_por_id(solicitacao_id)
    funcionarios = listar_funcionarios_por_solicitacao(
        solicitacao_id
    )

    if not solicitacao:
        return {"error": "Solicitação não encontrada"}

    return gerar_provisao(solicitacao, funcionarios)




