from flask import Blueprint, render_template, request
from app.services.pcp_service import resumo_dashboard, ranking_linhas_faltas_powerbi
from datetime import date
from app.services import cargos_service
from flask_login import login_required
from app.services.solicitacoes_service import obter_solicitacoes_abertas

bp = Blueprint("pages", __name__)

@bp.route("/")
@login_required
def inicio():
    return render_template("inicio.html", active_menu="inicio")

@bp.route("/dashboard")
@login_required
def dashboard():
    data_inicial = request.args.get("data_inicial")
    data_final = request.args.get("data_final")
    turno = request.args.get("turno")
    filial = request.args.get("filial")

    hoje = date.today().isoformat()
    if not data_inicial:
        data_inicial = hoje
    if not data_final:
        data_final = hoje

    filtros = {
        "data_inicial": data_inicial,
        "data_final": data_final,
        "turno": turno,
        "filial": filial
    }

    dados = resumo_dashboard(filtros)

    return render_template(
        "dashboard.html",
        filtros=filtros,
        active_menu="dashboard",
        **dados
    )

@bp.route("/cargos")
@login_required
def cargos():
    lista = cargos_service.listar()
    return render_template("cargos.html", cargos=lista)

@bp.route("/lancamento")
@login_required
def lancamento():
    cargos_tecnica = cargos_service.listar_por_area("TECNICA")
    cargos_producao = cargos_service.listar_por_area("PRODUCAO")

    return render_template(
        "lancamento.html",
        cargos_tecnica=cargos_tecnica,
        cargos_producao=cargos_producao
    )

@bp.route("/dashboard/linha/ferias", methods=["GET"])
@login_required
def ferias_linha():
    linha = request.args.get("linha")
    filtros = {
        "data_inicial": request.args.get("data_inicial"),
        "data_final": request.args.get("data_final"),
        "turno": request.args.get("turno"),
        "filial": request.args.get("filial")
    }
    return jsonify(ferias_por_linha(filtros))

@bp.route("/relatorios")
@login_required
def relatorios():
    return render_template("relatorios.html", active_menu="dashboard")

@bp.route("/powerbi")
@login_required
def powerbi():
    filtros = {
        "data_inicial": request.args.get("data_inicial"),
        "data_final": request.args.get("data_final"),
        "turno": request.args.get("turno"),
        "filial": request.args.get("filial"),
        "setor": request.args.get("setor"),
        "linha": request.args.get("linha"),
    }

    hoje = date.today().isoformat()
    filtros["data_inicial"] = filtros["data_inicial"] or hoje
    filtros["data_final"] = filtros["data_final"] or hoje
    
    dados = resumo_dashboard(filtros)
    
    ranking_faltas_powerbi = ranking_linhas_faltas_powerbi(filtros)
    
    return render_template(
        "powerbi.html",
        filtros=filtros,
        active_menu="dashboard",
        ranking_faltas_powerbi=ranking_faltas_powerbi,
        **dados
    )

@bp.route("/cargos/hc-linhas")
@login_required
def hc_linhas():
    return render_template(
        "hclinhas.html",
        active_menu="cargos"  
    )

@bp.route("/lancamento/atestados")
@login_required
def atestados():
    cargos_tecnica = cargos_service.listar_por_area("TECNICA")
    cargos_producao = cargos_service.listar_por_area("PRODUCAO")

    return render_template(
        "atestados.html",
        cargos_tecnica=cargos_tecnica,
        cargos_producao=cargos_producao,
        active_menu="lancamento"
    )

@bp.route("/login")
def login():
    return render_template("auth/login.html")

@bp.route("/solicitacoes")
@login_required
def solicitacoes():
    return render_template(
        "solicitacoes.html",
        active_menu="solicitacoes"
    )

@bp.route("/pedidos")
@login_required
def pedidos():
    solicitacoes = obter_solicitacoes_abertas()

    return render_template(
        "pedidos.html",
        solicitacoes=solicitacoes,
        active_menu="pedidos"
    )

@bp.route("/minhas-extras")
@login_required
def minhas_extras():
    return render_template("minhasextras.html", active_menu="minhasextras")


@bp.route("/solicitacoes/fechadas")
@login_required
def solicitacoes_fechadas():
    return render_template(
        "solicitacoes-fechadas.html",
        active_menu="solicitacoes"
    )


@bp.route("/solicitacoes/abertas")
@login_required
def solicitacoes_abertas():
    solicitacoes = obter_solicitacoes_abertas()

    return render_template(
        "solicitacoes-abertas.html",
        solicitacoes=solicitacoes,
        active_menu="solicitacoes"
    )



@bp.route("/solicitacoes/<int:solicitacao_id>")
@login_required
def solicitacao_detalhe(solicitacao_id):
    from app.services.solicitacoes_service import obter_detalhe_solicitacao

    dados = obter_detalhe_solicitacao(solicitacao_id)

    return render_template(
        "solicitacao_detalhe.html",
        **dados,
        active_menu="solicitacoes"
    )
