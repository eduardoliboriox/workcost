import json
from app.repositories.solicitacoes_repository import inserir_solicitacao, listar_solicitacoes_abertas


def criar_solicitacao(form):

    try:
        funcionarios = json.loads(form.get("funcionarios_json", "[]"))

        dados = {
            "data": form["data"],
            "turnos": ",".join(form.getlist("turnos")),
            "setores": ",".join(form.getlist("setores")),
            "cliente": form["cliente"],
            "descricao": form["descricao"],
            "atividades": form["atividades"]
        }

        inserir_solicitacao(dados, funcionarios)

        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}


def obter_solicitacoes_abertas():
    rows = listar_solicitacoes_abertas()

    resultado = []
    for r in rows:
        resultado.append({
            "id": r["id"],
            "data": r["data"],
            "solicitante": r["solicitante"],
            "descricao": r["atividades"],
            "status_solicitacao": (
                "Confirmado"
                if r["assinadas"] == r["total_aprovacoes"] and r["total_aprovacoes"] > 0
                else "Pendente"
            )
        })

    return resultado
