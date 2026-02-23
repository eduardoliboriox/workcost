from __future__ import annotations

from typing import Any


def resumo_powerbi_solicitacoes(filtros: dict) -> dict[str, Any]:
    """
    Camada de serviço do PowerBI.

    Responsabilidade:
    - Expor a função pública consumida por routes (pages/api)
    - Manter regra de negócio / agregação centralizada
    - Delegar a montagem do payload para o módulo já existente no repositório

    Observação:
    - Não existe "HC planejado/real" aqui por decisão do produto.
    - Foco: solicitações, extras, gastos, banco/compensação (se existirem dados),
      e faltas/frequência apenas como leitura complementar.
    """
    from app.repositories.powerbi_service import (
        resumo_powerbi_solicitacoes as repo_resumo_powerbi_solicitacoes,
    )

    return repo_resumo_powerbi_solicitacoes(filtros)
