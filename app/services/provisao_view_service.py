from app.repositories.solicitacoes_repository import (
    buscar_solicitacao_por_id,
    listar_funcionarios_por_solicitacao
)
from app.services.provisao_service import gerar_provisao


def gerar_provisao_para_template(solicitacao_id: int):

    solicitacao = buscar_solicitacao_por_id(solicitacao_id)
    if not solicitacao:
        return None

    funcionarios = listar_funcionarios_por_solicitacao(solicitacao_id)

    resultado = gerar_provisao(solicitacao, funcionarios)

    return {
        "solicitacao": solicitacao,
        "funcionarios": resultado["funcionarios"],
        "total_geral": resultado["total_geral"]
    }
