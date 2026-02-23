from __future__ import annotations

from datetime import date
from typing import Any


def _normalize_filtros(raw: dict) -> dict:
    """
    Normaliza filtros vindos de request.args para evitar None inesperado.
    Mantém compatibilidade com o que o template/JS já espera.
    """
    filtros = dict(raw or {})

    hoje = date.today().isoformat()

    filtros["data_inicial"] = filtros.get("data_inicial") or hoje
    filtros["data_final"] = filtros.get("data_final") or hoje

    # estes podem ser vazios mesmo
    filtros["turno"] = filtros.get("turno") or ""
    filtros["filial"] = filtros.get("filial") or ""
    filtros["setor"] = filtros.get("setor") or ""
    filtros["linha"] = filtros.get("linha") or ""

    return filtros


def resumo_powerbi_solicitacoes(filtros: dict) -> dict[str, Any]:
    """
    Fonte da verdade do PowerBI:
    - resumo_dashboard (kpis gerais e ranking por linha, etc)
    - ranking_linhas_faltas_powerbi (ranking de linhas por faltas)

    Retorna no formato que o frontend do powerbi já consome:
      {
        "filtros": ...,
        "kpis": ...,
        "ranking_faltas": [...]
      }
    """
    filtros = _normalize_filtros(filtros)

    # Import local para evitar import circular
    from app.services.pcp_service import (
        resumo_dashboard,
        ranking_linhas_faltas_powerbi,
    )

    resumo = resumo_dashboard(filtros)

    return {
        "filtros": filtros,
        "kpis": (resumo.get("kpis") or {}),
        "ranking_faltas": ranking_linhas_faltas_powerbi(filtros),
        # se o resumo_dashboard também devolve "dados" (cards/linhas),
        # repassamos sem acoplar o template a outro service
        "dados": resumo.get("dados") or resumo.get("linhas") or resumo.get("itens") or [],
    }
