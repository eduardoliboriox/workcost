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
    contar_presencas,
    contar_absenteismo_geral,
    contar_linhas_ativas,
    listar_objetivos_dashboard,
    listar_solicitacoes_para_ranking_cliente,
    listar_solicitacoes_para_ranking_tipo,
    listar_faltas_por_data
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

        roles_aprovados = all(
            aprov_map.get(r["id"], {}).get(role)
            for role in ROLES
        )

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

        data_execucao = r.get("data_execucao")

        if not data_execucao:
            continue

        if data_inicial and data_execucao < data_inicial:
            continue

        if data_final and data_execucao > data_final:
            continue

        turnos_solicitacao = [
            t.strip() for t in (r.get("turnos") or "").split(",")
        ]

        if turno_filtro and turno_filtro not in turnos_solicitacao:
            continue

        funcionarios = listar_funcionarios_por_solicitacao(r["id"])
        provisao = gerar_provisao(r, funcionarios)
        total = provisao["total_geral"]

        ranking[filial_valida]["quantidade"] += 1

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

        filiais_solicitacao = [
            f.strip() for f in (r.get("unidade") or "").split(",")
        ]

        if filial_filtro and filial_filtro not in filiais_solicitacao:
            continue

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

        unidades = [u.strip() for u in (r.get("unidade") or "").split(",")]
        if filial_filtro and filial_filtro not in unidades:
            continue

        turnos = [t.strip() for t in (r.get("turnos") or "").split(",")]
        if turno_filtro and turno_filtro not in turnos:
            continue

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


def ranking_solicitacoes_por_tipo(filtros: dict):

    from datetime import date
    from app.repositories.solicitacoes_repository import (
        listar_solicitacoes_para_ranking_tipo
    )

    data_inicial = filtros.get("data_inicial")
    data_final = filtros.get("data_final")
    turno_filtro = filtros.get("turno")
    filial_filtro = filtros.get("filial")

    if data_inicial:
        data_inicial = date.fromisoformat(data_inicial)

    if data_final:
        data_final = date.fromisoformat(data_final)

    rows = listar_solicitacoes_para_ranking_tipo()

    contagem = {}

    for r in rows:

        data_execucao = r.get("data_execucao")
        if not data_execucao:
            continue

        if data_inicial and data_execucao < data_inicial:
            continue

        if data_final and data_execucao > data_final:
            continue

        unidades = [u.strip() for u in (r.get("unidade") or "").split(",")]
        if filial_filtro and filial_filtro not in unidades:
            continue

        turnos = [t.strip() for t in (r.get("turnos") or "").split(",")]
        if turno_filtro and turno_filtro not in turnos:
            continue

        descricao = (r.get("descricao") or "").strip()

        if not descricao:
            continue

        contagem[descricao] = contagem.get(descricao, 0) + 1

    total = sum(contagem.values()) or 1

    resultado = [
        {
            "tipo": nome,
            "percentual": round((qtd / total) * 100, 2)
        }
        for nome, qtd in contagem.items()
    ]

    resultado.sort(key=lambda x: x["percentual"], reverse=True)

    return resultado


def resumo_solicitacoes_dashboard(filtros: dict):
    """
    KPIs do Dashboard referentes às solicitações:
    - Solicitações Abertas
    - Solicitações Realizadas
    - Total Gasto (provisão das fechadas)

    Respeita filtros globais:
    data_inicial, data_final, turno, filial
    """

    from datetime import date
    from app.repositories.solicitacoes_repository import (
        listar_solicitacoes_com_status,
        listar_funcionarios_por_solicitacao
    )
    from app.services.provisao_service import gerar_provisao

    hoje = date.today()

    data_inicial = filtros.get("data_inicial")
    data_final = filtros.get("data_final")
    turno_filtro = filtros.get("turno")
    filial_filtro = filtros.get("filial")

    if data_inicial:
        data_inicial = date.fromisoformat(data_inicial)

    if data_final:
        data_final = date.fromisoformat(data_final)

    rows = listar_solicitacoes_com_status()

    total_abertas = 0
    total_fechadas = 0
    total_gasto = 0.0

    for r in rows:

        data_execucao = r.get("data_execucao")
        if not data_execucao:
            continue

        if data_inicial and data_execucao < data_inicial:
            continue

        if data_final and data_execucao > data_final:
            continue

        unidades = [u.strip() for u in (r.get("unidade") or "").split(",")]
        if filial_filtro and filial_filtro not in unidades:
            continue

        turnos = [t.strip() for t in (r.get("turnos") or "").split(",")]
        if turno_filtro and turno_filtro not in turnos:
            continue

        if data_execucao > hoje:
            total_abertas += 1
            continue

        if data_execucao <= hoje:
            total_fechadas += 1

            funcionarios = listar_funcionarios_por_solicitacao(r["id"])
            provisao = gerar_provisao(r, funcionarios)
            total_gasto += provisao["total_geral"]

    return {
        "abertas": total_abertas,
        "fechadas": total_fechadas,
        "total_gasto": round(total_gasto, 2)
    }


def ranking_absenteismo_por_data(filtros: dict):

    from datetime import date
    from app.repositories.solicitacoes_repository import (
        listar_faltas_por_data
    )

    data_inicial = filtros.get("data_inicial")
    data_final = filtros.get("data_final")

    if data_inicial:
        data_inicial = date.fromisoformat(data_inicial)

    if data_final:
        data_final = date.fromisoformat(data_final)

    rows = listar_faltas_por_data()

    agrupado = {}

    for r in rows:

        data = r["data"]

        if data_inicial and data < data_inicial:
            continue

        if data_final and data > data_final:
            continue

        agrupado.setdefault(data, []).append({
            "matricula": r["matricula"],
            "nome": r["nome"],
            "total": r["total_faltas"]
        })

    resultado = []

    for data, funcionarios in agrupado.items():

        total_dia = sum(f["total"] for f in funcionarios)

        resultado.append({
            "data": data,
            "qtd": total_dia,
            "funcionarios": funcionarios
        })

    resultado.sort(key=lambda x: x["data"], reverse=True)

    return resultado


def _clientes_ativos_kpi(filtros: dict) -> int:
    """
    KPI: Clientes Ativos
    - Não usa "linhas ativas" (não existe informação confiável por linha).
    - Conta clientes únicos dentro do recorte de filtros globais.
    - Como 'cliente' pode vir multi-valor (CSV), splitamos e deduplicamos via set.
    """

    from datetime import date

    data_inicial = filtros.get("data_inicial")
    data_final = filtros.get("data_final")
    turno_filtro = filtros.get("turno")
    filial_filtro = filtros.get("filial")

    if data_inicial:
        data_inicial = date.fromisoformat(data_inicial)

    if data_final:
        data_final = date.fromisoformat(data_final)

    rows = listar_solicitacoes_para_ranking_cliente()

    ativos = set()

    for r in rows:
        data_execucao = r.get("data_execucao")
        if not data_execucao:
            continue

        if data_inicial and data_execucao < data_inicial:
            continue

        if data_final and data_execucao > data_final:
            continue

        unidades = [u.strip() for u in (r.get("unidade") or "").split(",")]
        if filial_filtro and filial_filtro not in unidades:
            continue

        turnos = [t.strip() for t in (r.get("turnos") or "").split(",")]
        if turno_filtro and turno_filtro not in turnos:
            continue

        clientes = [c.strip() for c in (r.get("cliente") or "").split(",")]
        for c in clientes:
            if c:
                ativos.add(c)

    return len(ativos)


def kpis_dashboard_abs_linhas(filtros: dict):
    """
    KPIs do dashboard:
    - absenteismo (%): baseado na solicitacao_frequencia
    - linhas (int): **agora representa CLIENTES ATIVOS** (por compatibilidade de chave/JS/template)

    Respeita filtros globais:
    data_inicial, data_final, turno, filial
    """

    data_inicial = filtros.get("data_inicial") or None
    data_final = filtros.get("data_final") or None

    turno = filtros.get("turno") or None
    filial = filtros.get("filial") or None

    total_registros, total_faltas = contar_absenteismo_geral(
        data_inicial=data_inicial,
        data_final=data_final,
        turno=turno,
        filial=filial
    )

    if total_registros <= 0:
        abs_percent = 0.0
    else:
        abs_percent = round((total_faltas / total_registros) * 100, 1)

    clientes_ativos = _clientes_ativos_kpi(filtros)

    return {
        "absenteismo": abs_percent,
        "linhas": clientes_ativos
    }


def ranking_gastos_provisao_dashboard(filtros: dict):

    from datetime import date
    from app.repositories.solicitacoes_repository import listar_solicitacoes_com_status
    from app.services.relatorios_service import gerar_provisao_gastos_extra

    data_inicial = filtros.get("data_inicial")
    data_final = filtros.get("data_final")
    turno_filtro = filtros.get("turno")
    filial_filtro = filtros.get("filial")

    if data_inicial:
        data_inicial = date.fromisoformat(data_inicial)

    if data_final:
        data_final = date.fromisoformat(data_final)

    rows = listar_solicitacoes_com_status()

    totais = {}

    def _add(tipo: str, valor: float):
        if not tipo:
            return
        totais[tipo] = float(totais.get(tipo, 0.0)) + float(valor or 0.0)

    def _normalizar_gastos(payload):

        if payload is None:
            return []

        if isinstance(payload, list):
            return payload

        if isinstance(payload, dict):
            if isinstance(payload.get("gastos"), list):
                return payload["gastos"]

            itens = []
            for k, v in payload.items():
                if isinstance(v, (int, float)) and isinstance(k, str):
                    itens.append({"tipo": k, "valor": v})
            return itens

        return []

    for r in rows:
        solicitacao_id = r.get("id")
        data_execucao = r.get("data_execucao")
        if not solicitacao_id or not data_execucao:
            continue

        if data_inicial and data_execucao < data_inicial:
            continue

        if data_final and data_execucao > data_final:
            continue

        unidades = [u.strip() for u in (r.get("unidade") or "").split(",")]
        if filial_filtro and filial_filtro not in unidades:
            continue

        turnos = [t.strip() for t in (r.get("turnos") or "").split(",")]
        if turno_filtro and turno_filtro not in turnos:
            continue

        gastos_payload = gerar_provisao_gastos_extra(solicitacao_id)
        gastos = _normalizar_gastos(gastos_payload)

        for item in gastos:
            if not isinstance(item, dict):
                continue

            tipo = (
                item.get("tipo")
                or item.get("nome")
                or item.get("descricao")
                or ""
            )
            valor = (
                item.get("valor")
                or item.get("total")
                or item.get("valor_total")
                or 0
            )

            try:
                _add(str(tipo).strip(), float(valor or 0))
            except Exception:
                continue

    total_geral = sum(totais.values()) or 0.0

    resultado = []
    for tipo, total in totais.items():
        percentual = 0.0 if total_geral <= 0 else round((total / total_geral) * 100, 1)
        resultado.append({
            "tipo": tipo,
            "percentual": percentual,
            "total": round(float(total), 2)
        })

    resultado.sort(key=lambda x: x["total"], reverse=True)
    return resultado


# =========================================================
# DASHBOARD — COMPOSIÇÃO DA PROVISÃO (provisao_service.py)
# =========================================================

def ranking_tipos_provisao_dashboard(filtros: dict):
    """
    Card financeiro (provisões) baseado em app/services/provisao_service.py

    Mostra a composição por:
    - Refeição
    - Transporte
    - Adicional Noturno

    Respeita filtros globais:
    data_inicial, data_final, turno, filial
    """

    from datetime import date
    from app.repositories.solicitacoes_repository import (
        listar_solicitacoes_com_status,
        listar_funcionarios_por_solicitacao
    )
    from app.services.provisao_service import gerar_provisao

    data_inicial = filtros.get("data_inicial")
    data_final = filtros.get("data_final")
    turno_filtro = filtros.get("turno")
    filial_filtro = filtros.get("filial")

    if data_inicial:
        data_inicial = date.fromisoformat(data_inicial)

    if data_final:
        data_final = date.fromisoformat(data_final)

    rows = listar_solicitacoes_com_status()

    totais = {
        "Refeição": 0.0,
        "Transporte": 0.0,
        "Adicional Noturno": 0.0
    }

    for r in rows:

        data_execucao = r.get("data_execucao")
        if not data_execucao:
            continue

        if data_inicial and data_execucao < data_inicial:
            continue

        if data_final and data_execucao > data_final:
            continue

        unidades = [u.strip() for u in (r.get("unidade") or "").split(",")]
        if filial_filtro and filial_filtro not in unidades:
            continue

        turnos = [t.strip() for t in (r.get("turnos") or "").split(",")]
        if turno_filtro and turno_filtro not in turnos:
            continue

        funcionarios = listar_funcionarios_por_solicitacao(r["id"])
        provisao = gerar_provisao(r, funcionarios)

        for f in (provisao.get("funcionarios") or []):
            totais["Refeição"] += float(f.get("custo_refeicao") or 0.0)
            totais["Transporte"] += float(f.get("custo_transporte") or 0.0)
            totais["Adicional Noturno"] += float(f.get("adicional_noturno") or 0.0)

    total_geral = sum(totais.values()) or 0.0

    resultado = []
    for tipo, total in totais.items():
        percentual = 0.0 if total_geral <= 0 else round((total / total_geral) * 100, 1)
        resultado.append({
            "tipo": tipo,
            "percentual": percentual,
            "total": round(float(total), 2)
        })

    resultado.sort(key=lambda x: x["total"], reverse=True)
    return resultado
