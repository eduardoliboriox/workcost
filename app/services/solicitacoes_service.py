import json
from app.repositories.solicitacoes_repository import inserir_solicitacao


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
