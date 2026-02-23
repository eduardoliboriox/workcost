from __future__ import annotations

from typing import Any, Dict, List

from app.services.solicitacoes_service import (
    resumo_solicitacoes_dashboard,
    ranking_extras_dashboard,
    ranking_solicitacoes_por_cliente,
    ranking_solicitacoes_por_tipo,
    kpis_dashboard_abs_linhas,
    ranking_absenteismo_por_data,
)


def _base_filters(filtros: dict) -> dict:
    """
    Normaliza os filtros para o que realmente existe em 'solicitacoes'.

    Observação:
    - PowerBI antigo tinha setor/linha (PCP). Para solicitacoes, hoje usamos:
      data_inicial, data_final, turno, filial.
    - Se vierem setor/linha, são ignorados aqui (sem quebrar o form).
    """
    return {
        "data_inicial": filtros.get("data_inicial"),
        "data_final": filtros.get("data_final"),
        "turno": filtros.get("turno"),
        "filial": filtros.get("filial"),
    }


def resumo_powerbi_solicitacoes(filtros: dict) -> Dict[str, Any]:
    """
    Resumo consolidado para a página Power BI focada em Solicitações.
    Retorna:
      - kpis (solicitacoes + abs + linhas + extras totals)
      - rankings (extras, clientes, tipos, abs_por_data)
    """
    f = _base_filters(filtros)

    kpis_solic = resumo_solicitacoes_dashboard(f)
    kpis_abs = kpis_dashboard_abs_linhas(f)

    ranking_extras = ranking_extras_dashboard(f)
    ranking_clientes = ranking_solicitacoes_por_cliente(f)
    ranking_tipos = ranking_solicitacoes_por_tipo(f)

    # absenteísmo por data usa só data_inicial/data_final
    abs_por_data = ranking_absenteismo_por_data({
        "data_inicial": f.get("data_inicial"),
        "data_final": f.get("data_final"),
    })

    # Totais de extras (provisionado/realizado) somando o ranking por unidade
    total_extras_provisionado = round(
        sum(float(x.get("provisionado") or 0) for x in ranking_extras), 2
    )
    total_extras_realizado = round(
        sum(float(x.get("realizado") or 0) for x in ranking_extras), 2
    )

    # KPI extra: volume de extras em % por unidade já existe via ranking_extras,
    # mas aqui queremos totais em R$ para diretoria/gestores.
    kpis = {
        "solicitacoes_abertas": int(kpis_solic.get("abertas") or 0),
        "solicitacoes_realizadas": int(kpis_solic.get("fechadas") or 0),
        "total_gasto": float(kpis_solic.get("total_gasto") or 0.0),

        "extras_provisionado": float(total_extras_provisionado),
        "extras_realizado": float(total_extras_realizado),

        "absenteismo": float(kpis_abs.get("absenteismo") or 0.0),
        "linhas": int(kpis_abs.get("linhas") or 0),
    }

    return {
        "kpis": kpis,
        "rankings": {
            "extras": ranking_extras,
            "clientes": ranking_clientes,
            "tipos": ranking_tipos,
            "abs_por_data": abs_por_data,
        }
    }
