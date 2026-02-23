from __future__ import annotations

from datetime import date
from typing import Any


def _normalize_filtros(raw: dict | None) -> dict[str, Any]:
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


def resumo_powerbi_solicitacoes(filtros: dict | None) -> dict[str, Any]:
    """
    PowerBI (Gestores) — foco no sistema de solicitações:
    - KPIs de solicitações (abertas/realizadas/total gasto)
    - KPIs complementares (extras provisionado/realizado, absenteismo, linhas ativas)
    - Rankings (clientes, extras por unidade, tipos)

    Retorno padronizado:
      {
        "filtros": {...},
        "kpis": {...},
        "rankings": {
          "clientes": [...],
          "extras": [...],
          "tipos": [...]
        }
      }
    """
    filtros = _normalize_filtros(filtros)

    from app.services.solicitacoes_service import (
        ranking_extras_dashboard,
        ranking_solicitacoes_por_cliente,
        ranking_solicitacoes_por_tipo,
        resumo_solicitacoes_dashboard,
        kpis_dashboard_abs_linhas,
    )

    sol = resumo_solicitacoes_dashboard(filtros)
    extras = ranking_extras_dashboard(filtros)
    extras_provisionado = round(
        sum(float(x.get("provisionado") or 0) for x in (extras or [])),
        2,
    )
    extras_realizado = round(
        sum(float(x.get("realizado") or 0) for x in (extras or [])),
        2,
    )

    abs_linhas = kpis_dashboard_abs_linhas(filtros)

    clientes = ranking_solicitacoes_por_cliente(filtros)
    tipos = ranking_solicitacoes_por_tipo(filtros)

    kpis = {
        "solicitacoes_abertas": int(sol.get("abertas") or 0),
        "solicitacoes_realizadas": int(sol.get("fechadas") or 0),
        "total_gasto": float(sol.get("total_gasto") or 0.0),
        "extras_provisionado": float(extras_provisionado),
        "extras_realizado": float(extras_realizado),
        "absenteismo": float(abs_linhas.get("absenteismo") or 0.0),
        "linhas": int(abs_linhas.get("linhas") or 0),
    }

    return {
        "filtros": filtros,
        "kpis": kpis,
        "rankings": {
            "clientes": clientes or [],
            "extras": extras or [],
            "tipos": tipos or [],
        },
    }
