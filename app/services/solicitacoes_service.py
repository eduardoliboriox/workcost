import json
from app.repositories.solicitacoes_repository import (
    inserir_solicitacao,
    listar_solicitacoes_abertas,
    listar_aprovacoes_por_solicitacao, 
    buscar_solicitacao_por_id,
    listar_funcionarios_por_solicitacao,
    listar_aprovacoes_por_solicitacao_id,
    registrar_aprovacao, 
    registrar_assinatura_funcionario
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

        total_funcionarios = r["total_funcionarios"]
        assinadas = r["assinadas"]

        resultado.append({
            "id": r["id"],
            "data": r["data"],
            "solicitante": r["solicitante"],
            "descricao": r["atividades"],
            "status_solicitacao": (
                "Confirmado"
                if total_funcionarios > 0 and assinadas == total_funcionarios
                else "Pendente"
            ),
            "aprovacoes": status_roles
        })

    return resultado


def obter_detalhe_solicitacao(solicitacao_id: int):
    solicitacao = buscar_solicitacao_por_id(solicitacao_id)

    funcionarios = listar_funcionarios_por_solicitacao(solicitacao_id)
    aprovacoes = listar_aprovacoes_por_solicitacao_id(solicitacao_id)

    aprov_map = {a["role"]: a for a in aprovacoes}

    return {
        "solicitacao": solicitacao,
        "funcionarios": funcionarios,
        "aprovacoes": aprov_map
    }


def aprovar_solicitacao(solicitacao_id: int, role: str):
    registrar_aprovacao(
        solicitacao_id=solicitacao_id,
        user_id=current_user.id,
        role=role
    )


def confirmar_presenca_funcionario(
    solicitacao_id: int,
    matricula: str,
    password: str
):
    from app.auth.service import confirm_employee_extra
    from app.repositories.solicitacoes_repository import (
        listar_funcionarios_por_solicitacao
    )

    result = confirm_employee_extra(matricula, password)
    if not result["success"]:
        return result

    registrar_assinatura_funcionario(
        solicitacao_id=solicitacao_id,
        matricula=matricula,
        username=result["username"]
    )

    # 🔑 Fonte da verdade: banco
    funcionarios = listar_funcionarios_por_solicitacao(solicitacao_id)

    funcionario = next(
        f for f in funcionarios
        if f["matricula"].lstrip("0") == matricula.lstrip("0")
    )
    
    return {
        "success": True,
        "signed_by": funcionario["signed_by"],
        "signed_at": funcionario["signed_at"].isoformat()
        if funcionario.get("signed_at") else None
    }



def salvar_view_solicitacao(
    solicitacao_id: int,
    aprovacoes: list,
    funcionarios: list
):
    """
    Commit explícito do modo VIEW.
    Nada aqui valida senha.
    Apenas persiste o que já foi confirmado no frontend.
    """

    for a in aprovacoes:
        registrar_aprovacao(
            solicitacao_id=solicitacao_id,
            user_id=current_user.id,
            role=a["role"]
        )

    for f in funcionarios:
        registrar_assinatura_funcionario(
            solicitacao_id=solicitacao_id,
            matricula=f["matricula"],
            username=f["username"]
        )
