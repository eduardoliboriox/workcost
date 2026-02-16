import json
from app.repositories.solicitacoes_repository import (
    inserir_solicitacao,
    listar_solicitacoes_abertas,
    listar_aprovacoes_por_solicitacao, 
    buscar_solicitacao_por_id,
    listar_funcionarios_por_solicitacao,
    listar_aprovacoes_por_solicitacao_id,
    registrar_aprovacao, 
    registrar_assinatura_funcionario,
    listar_solicitacoes_abertas_por_matricula, 
    atualizar_recebido_em,
    atualizar_lancado_em,
    deletar_solicitacao_por_id, 
    listar_solicitacoes_com_status,
    listar_frequencia_por_solicitacao,
    salvar_frequencia,
    contar_presencas
)
from flask_login import current_user
from datetime import date, timedelta


ROLES = ["gestor", "gerente", "controladoria", "diretoria", "rh"]


def criar_solicitacao(form):

    try:
        funcionarios = json.loads(form.get("funcionarios_json", "[]"))

        dados = {
            "data": form["data"],
            "data_execucao": form.get("data_execucao"),
            "turnos": ",".join(form.getlist("turnos")),
            "unidade": form.get("unidade"),   
            "setores": ",".join(form.getlist("setores")),
            "cliente": ",".join(form.getlist("clientes")),
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
            "data_execucao": r["data_execucao"],
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
    funcionarios: list,
    recebido_em: str | None = None,
    lancado_em: str | None = None
):
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

    if recebido_em:
        atualizar_recebido_em(solicitacao_id, recebido_em)

    if lancado_em:
        atualizar_lancado_em(solicitacao_id, lancado_em)


def obter_minhas_extras(matricula: str):
    rows = listar_solicitacoes_abertas_por_matricula(matricula)
    aprovacoes = listar_aprovacoes_por_solicitacao()

    aprov_map = {}
    for a in aprovacoes:
        aprov_map.setdefault(a["solicitacao_id"], {})[a["role"]] = a

    resultado = []

    for r in rows:
        status_roles = {}

        for role in ROLES:
            aprovado = aprov_map.get(r["id"], {}).get(role)
            status_roles[role] = aprovado["username"] if aprovado else None

        resultado.append({
            "id": r["id"],
            "data": r["data"],
            "data_execucao": r["data_execucao"],
            "solicitante": r["solicitante"],
            "descricao": r["atividades"],
            "status_solicitacao": (
                "Confirmado"
                if r["total_funcionarios"] > 0
                and r["assinadas"] == r["total_funcionarios"]
                else "Pendente"
            ),
            "aprovacoes": status_roles
        })

    return resultado

def excluir_solicitacao(solicitacao_id: int):
    """
    Exclusão definitiva da solicitação.
    Apenas admins podem executar.
    """

    if not current_user.is_admin:
        return {"success": False, "error": "Sem permissão"}

    deletar_solicitacao_por_id(solicitacao_id)

    return {"success": True}


def obter_solicitacoes_fechadas():
    rows = listar_solicitacoes_com_status()
    aprovacoes = listar_aprovacoes_por_solicitacao()

    aprov_map = {}
    for a in aprovacoes:
        aprov_map.setdefault(a["solicitacao_id"], {})[a["role"]] = a

    resultado = []
    hoje = date.today()

    for r in rows:

        total_funcionarios = r["total_funcionarios"]
        assinadas = r["assinadas"]

        # todos roles aprovados?
        roles_aprovados = all(
            aprov_map.get(r["id"], {}).get(role)
            for role in ROLES
        )

        # regra fechamento
        if (
            r["data_execucao"]
            and total_funcionarios > 0
            and assinadas == total_funcionarios
            and roles_aprovados
            and hoje > r["data_execucao"]
        ):

            efetivo_real = contar_presencas(r["id"])
            
            resultado.append({
                "id": r["id"],
                "data": r["data"],
                "data_execucao": r["data_execucao"],
                "solicitante": r["solicitante"],
                "efetivo_previsto": total_funcionarios,
                "efetivo_real": efetivo_real,
                "objetivo_status": r.get("objetivo_status"),
                "observacoes": r.get("observacoes")
            })

    return resultado

def obter_frequencia(solicitacao_id: int):
    funcionarios = listar_funcionarios_por_solicitacao(solicitacao_id)
    frequencias = listar_frequencia_por_solicitacao(solicitacao_id)

    freq_map = {f["matricula"]: f["compareceu"] for f in frequencias}

    resultado = []

    for f in funcionarios:
        resultado.append({
            "matricula": f["matricula"],
            "nome": f["nome"],
            "compareceu": freq_map.get(f["matricula"], True)
        })

    return resultado


def salvar_frequencia_service(solicitacao_id: int, dados: list):
    for item in dados:
        salvar_frequencia(
            solicitacao_id,
            item["matricula"],
            item["compareceu"]
        )

    return {"success": True}


def salvar_fechamento_solicitacao(
    solicitacao_id: int,
    objetivo_status: str,
    observacoes: str
):
    from app.repositories.solicitacoes_repository import (
        atualizar_fechamento
    )

    atualizar_fechamento(
        solicitacao_id,
        objetivo_status,
        observacoes
    )

    return {"success": True}


def ranking_extras_dashboard(filtros: dict):

    from datetime import date
    from app.repositories.solicitacoes_repository import (
        listar_solicitacoes_com_status
    )
    from app.repositories.solicitacoes_repository import (
        listar_funcionarios_por_solicitacao
    )
    from app.services.provisao_service import gerar_provisao

    hoje = date.today()
    FILIAIS_VALIDAS = ["VAC", "VTE", "VTT"]

    data_inicial = filtros.get("data_inicial")
    data_final = filtros.get("data_final")
    turno_filtro = filtros.get("turno")
    filial_filtro = filtros.get("filial")

    if data_inicial:
        data_inicial = date.fromisoformat(data_inicial)

    if data_final:
        data_final = date.fromisoformat(data_final)

    rows = listar_solicitacoes_com_status()

    ranking = {
        filial: {
            "quantidade": 0,
            "provisionado": 0,
            "realizado": 0
        }
        for filial in FILIAIS_VALIDAS
    }

    for r in rows:

        # ================================
        # FILTRAR UNIDADE
        # ================================
        filiais_solicitacao = [
            f.strip() for f in (r.get("unidade") or "").split(",")
        ]

        filial_valida = next(
            (f for f in filiais_solicitacao if f in FILIAIS_VALIDAS),
            None
        )

        if not filial_valida:
            continue

        if filial_filtro and filial_valida != filial_filtro:
            continue

        # ================================
        # FILTRAR DATA EXECUÇÃO
        # ================================
        data_execucao = r.get("data_execucao")

        if not data_execucao:
            continue

        if data_inicial and data_execucao < data_inicial:
            continue

        if data_final and data_execucao > data_final:
            continue

        # ================================
        # FILTRAR TURNO
        # ================================
        turnos_solicitacao = [
            t.strip() for t in (r.get("turnos") or "").split(",")
        ]

        if turno_filtro and turno_filtro not in turnos_solicitacao:
            continue

        # ================================
        # CALCULAR PROVISÃO REAL
        # ================================
        funcionarios = listar_funcionarios_por_solicitacao(r["id"])
        provisao = gerar_provisao(r, funcionarios)
        total = provisao["total_geral"]

        ranking[filial_valida]["quantidade"] += 1

        # ================================
        # REGRA SIMPLES
        # ================================
        if data_execucao > hoje:
            ranking[filial_valida]["provisionado"] += total
        else:
            ranking[filial_valida]["realizado"] += total

    total_extras = sum(v["quantidade"] for v in ranking.values()) or 1

    resultado = []

    for filial in FILIAIS_VALIDAS:

        valores = ranking[filial]

        percentual = round(
            (valores["quantidade"] / total_extras) * 100,
            1
        )

        resultado.append({
            "filial": filial,
            "percentual": percentual,
            "provisionado": round(valores["provisionado"], 2),
            "realizado": round(valores["realizado"], 2)
        })

    resultado.sort(key=lambda x: x["percentual"], reverse=True)

    return resultado

def objetivos_status_dashboard(filtros: dict):

    from datetime import date
    from app.repositories.solicitacoes_repository import (
        listar_objetivos_dashboard
    )

    data_inicial = filtros.get("data_inicial")
    data_final = filtros.get("data_final")
    turno_filtro = filtros.get("turno")
    filial_filtro = filtros.get("filial")

    if data_inicial:
        data_inicial = date.fromisoformat(data_inicial)

    if data_final:
        data_final = date.fromisoformat(data_final)

    rows = listar_objetivos_dashboard()

    contagem = {
        "nao": 0,
        "parcialmente": 0,
        "sim": 0
    }

    for r in rows:

        data_execucao = r.get("data_execucao")
        if not data_execucao:
            continue

        if data_inicial and data_execucao < data_inicial:
            continue

        if data_final and data_execucao > data_final:
            continue

        # FILTRO FILIAL
        filiais_solicitacao = [
            f.strip() for f in (r.get("unidade") or "").split(",")
        ]

        if filial_filtro and filial_filtro not in filiais_solicitacao:
            continue

        # FILTRO TURNO
        turnos_solicitacao = [
            t.strip() for t in (r.get("turnos") or "").split(",")
        ]

        if turno_filtro and turno_filtro not in turnos_solicitacao:
            continue

        status = (r.get("objetivo_status") or "").lower()

        if status in contagem:
            contagem[status] += 1

    total = sum(contagem.values()) or 1

    return [
        {
            "status": "Não",
            "percentual": round((contagem["nao"] / total) * 100, 2)
        },
        {
            "status": "Parcialmente",
            "percentual": round((contagem["parcialmente"] / total) * 100, 2)
        },
        {
            "status": "Sim",
            "percentual": round((contagem["sim"] / total) * 100, 2)
        }
    ]

def ranking_solicitacoes_por_cliente(filtros: dict):

    from datetime import date
    from app.repositories.solicitacoes_repository import (
        listar_solicitacoes_para_ranking_cliente
    )

    data_inicial = filtros.get("data_inicial")
    data_final = filtros.get("data_final")
    turno_filtro = filtros.get("turno")
    filial_filtro = filtros.get("filial")

    if data_inicial:
        data_inicial = date.fromisoformat(data_inicial)

    if data_final:
        data_final = date.fromisoformat(data_final)

    rows = listar_solicitacoes_para_ranking_cliente()

    contagem = {}

    for r in rows:

        data_execucao = r.get("data_execucao")
        if not data_execucao:
            continue

        if data_inicial and data_execucao < data_inicial:
            continue

        if data_final and data_execucao > data_final:
            continue

        # filtro unidade
        unidades = [u.strip() for u in (r.get("unidade") or "").split(",")]
        if filial_filtro and filial_filtro not in unidades:
            continue

        # filtro turno
        turnos = [t.strip() for t in (r.get("turnos") or "").split(",")]
        if turno_filtro and turno_filtro not in turnos:
            continue

        # pode haver múltiplos clientes
        clientes = [c.strip() for c in (r.get("cliente") or "").split(",")]

        for cliente in clientes:
            if not cliente:
                continue
            contagem[cliente] = contagem.get(cliente, 0) + 1

    total = sum(contagem.values()) or 1

    resultado = [
        {
            "cliente": nome,
            "percentual": round((qtd / total) * 100, 2)
        }
        for nome, qtd in contagem.items()
    ]

    resultado.sort(key=lambda x: x["percentual"], reverse=True)

    return resultado
