import json
from app.repositories.solicitacoes_repository import (
    inserir_solicitacao,
    listar_solicitacoes_abertas,
    listar_aprovacoes_por_solicitacao
)
from flask_login import current_user


ROLES = ["gestor", "gerente", "controladoria", "diretoria", "rh"]

def criar_solicitacao(form):

    try:
        funcionarios = json.loads(form.get("funcionarios_json", "[]"))

        dados = {
            "data": form["data"],
            "turnos": ",".join(form.getlist("turnos")),
            "setores": ",".join(form.getlist("setores")),
            "cliente": form["cliente"],
            "descricao": form["descricao"],
            "atividades": form["atividades"],
            "solicitante_user_id": current_user.id
        }

        inserir_solicitacao(dados, funcionarios)

        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}


def obter_solicitacoes_abertas():
    rows = listar_solicitacoes_abertas()
    aprovacoes = listar_aprovacoes_por_solicitacao()

    aprov_map = {}
    for a in aprovacoes:
        aprov_map.setdefault(a["solicitacao_id"], {})[a["role"]] = a

    resultado = []

    for r in rows:
        status_roles = {}

        for role in ROLES:
            aprovado = aprov_map.get(r["id"], {}).get(role)
            status_roles[role] = (
                aprovado["username"]
                if aprovado
                else None
            )

        resultado.append({
            "id": r["id"],
            "data": r["data"],
            "solicitante": r["solicitante"],
            "descricao": r["atividades"],
            "status_solicitacao": (
                "Confirmado"
                if r["assinadas"] == r["total_aprovacoes"] and r["total_aprovacoes"] > 0
                else "Pendente"
            ),
            "aprovacoes": status_roles
        })

    return resultado
