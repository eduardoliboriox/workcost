from flask import Blueprint, render_template, request
from datetime import date
from flask_login import login_required, current_user
from app.services.powerbi_service import resumo_powerbi_solicitacoes
from app.services.pcp_service import resumo_dashboard, ranking_linhas_faltas_powerbi
from app.services.solicitacoes_service import (
    obter_solicitacoes_abertas,
    ranking_extras_dashboard,
    objetivos_status_dashboard,
    ranking_solicitacoes_por_cliente,
    kpis_dashboard_abs_linhas,
    ranking_gastos_provisao_dashboard
)

bp = Blueprint("pages", __name__)

@bp.route("/")
@login_required
def inicio():
    return render_template("inicio.html", active_menu="inicio")

@bp.route("/dashboard")
@login_required
def dashboard():

    from datetime import date
    from calendar import monthrange
    from app.services.solicitacoes_service import ranking_extras_dashboard

    data_inicial = request.args.get("data_inicial")
    data_final = request.args.get("data_final")
    turno = request.args.get("turno")
    filial = request.args.get("filial")

    hoje = date.today()
    primeiro_dia_mes = date(hoje.year, hoje.month, 1)
    ultimo_dia_mes = date(
        hoje.year,
        hoje.month,
        monthrange(hoje.year, hoje.month)[1]
    )

    if not data_inicial:
        data_inicial = primeiro_dia_mes.isoformat()

    if not data_final:
        data_final = ultimo_dia_mes.isoformat()

    filtros = {
        "data_inicial": data_inicial,
        "data_final": data_final,
        "turno": turno,
        "filial": filial
    }

    dados = resumo_dashboard(filtros)
    ranking_extras = ranking_extras_dashboard(filtros)
    ranking_objetivos = objetivos_status_dashboard(filtros)
    ranking_clientes = ranking_solicitacoes_por_cliente(filtros)
    ranking_gastos = ranking_gastos_provisao_dashboard(filtros)

    kpis_fix = kpis_dashboard_abs_linhas(filtros)
    dados.setdefault("kpis", {})
    dados["kpis"]["absenteismo"] = kpis_fix["absenteismo"]
    dados["kpis"]["linhas"] = kpis_fix["linhas"]

    return render_template(
        "dashboard.html",
        filtros=filtros,
        ranking_extras=ranking_extras,
        ranking_objetivos=ranking_objetivos,
        ranking_clientes=ranking_clientes,
        ranking_gastos=ranking_gastos,
        active_menu="dashboard",
        **dados
    )

@bp.route("/lancamento")
@login_required
def lancamento():
    from app.services import cargos_service

    cargos_tecnica = cargos_service.listar_por_area("TECNICA")
    cargos_producao = cargos_service.listar_por_area("PRODUCAO")

    return render_template(
        "lancamento.html",
        cargos_tecnica=cargos_tecnica,
        cargos_producao=cargos_producao
    )

@bp.route("/relatorios")
@login_required
def relatorios():
    return render_template("relatorios.html", active_menu="dashboard")

@bp.route("/powerbi")
@login_required
def powerbi():
    from calendar import monthrange

    data_inicial = request.args.get("data_inicial")
    data_final = request.args.get("data_final")

    hoje = date.today()
    primeiro_dia_mes = date(hoje.year, hoje.month, 1)
    ultimo_dia_mes = date(
        hoje.year,
        hoje.month,
        monthrange(hoje.year, hoje.month)[1]
    )

    if not data_inicial:
        data_inicial = primeiro_dia_mes.isoformat()

    if not data_final:
        data_final = ultimo_dia_mes.isoformat()

    filtros = {
        "data_inicial": data_inicial,
        "data_final": data_final,
        "turno": request.args.get("turno"),
        "filial": request.args.get("filial"),
        "setor": request.args.get("setor"),
        "linha": request.args.get("linha"),
    }

    data = resumo_powerbi_solicitacoes(filtros)

    return render_template(
        "powerbi.html",
        filtros=data["filtros"],
        active_menu="dashboard",
        kpis=data["kpis"],
        rankings=data.get("rankings", {}),
        dados=[],
        ranking_faltas_powerbi=[],
        ranking_linhas_faltas_powerbi=[]
    )

@bp.route("/solicitacoes")
@login_required
def solicitacoes():
    return render_template(
        "solicitacoes.html",
        modo="create",
        aprovacoes={},
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
    from app.services.solicitacoes_service import obter_minhas_extras

    solicitacoes = obter_minhas_extras(current_user.matricula)

    return render_template(
        "minhasextras.html",
        solicitacoes=solicitacoes,
        active_menu="minhasextras"
    )

@bp.route("/solicitacoes/fechadas")
@login_required
def solicitacoes_fechadas():

    from app.services.solicitacoes_service import (
        obter_solicitacoes_fechadas
    )

    solicitacoes = obter_solicitacoes_fechadas()

    return render_template(
        "solicitacoes-fechadas.html",
        solicitacoes=solicitacoes,
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
def solicitacao_view(solicitacao_id):
    from app.services.solicitacoes_service import obter_detalhe_solicitacao

    dados = obter_detalhe_solicitacao(solicitacao_id)
    origem = request.args.get("from")

    active_menu = "solicitacoes"
    if origem == "pedidos":
        active_menu = "pedidos"
    elif origem == "minhasextras":
        active_menu = "minhasextras"

    return render_template(
        "solicitacoes.html",
        modo="view",
        solicitacao=dados["solicitacao"],
        funcionarios=dados["funcionarios"],
        aprovacoes=dados["aprovacoes"],
        active_menu=active_menu,
        origem=origem
    )

# ==============================
# LEGAL PAGES
# ==============================

@bp.route("/privacy-policy")
def privacy_policy():
    return render_template("legal/privacy.html")

@bp.route("/cookie-policy")
def cookie_policy():
    return render_template("legal/cookies.html")


@bp.route("/solicitacoes/<int:solicitacao_id>/provisao")
@login_required
def solicitacao_provisao(solicitacao_id):
    from app.services.provisao_view_service import (
        gerar_provisao_para_template
    )

    dados = gerar_provisao_para_template(solicitacao_id)

    if not dados:
        return "Solicitação não encontrada", 404

    origem = request.args.get("from")

    active_menu = "solicitacoes"
    if origem == "pedidos":
        active_menu = "pedidos"
    elif origem == "minhasextras":
        active_menu = "minhasextras"

    return render_template(
        "solicitacoes-provisao.html",
        solicitacao=dados["solicitacao"],
        funcionarios=dados["funcionarios"],
        total_geral=dados["total_geral"],
        active_menu=active_menu
    )


@bp.route("/solicitacoes/<int:solicitacao_id>/documento")
@login_required
def solicitacao_documento(solicitacao_id):

    from app.services.solicitacoes_service import obter_detalhe_solicitacao
    from app.services.provisao_view_service import gerar_provisao_para_template

    detalhe = obter_detalhe_solicitacao(solicitacao_id)
    provisao = gerar_provisao_para_template(solicitacao_id)

    if not detalhe:
        return "Solicitação não encontrada", 404

    return render_template(
        "solicitacoes.html",
        modo="view",
        solicitacao=detalhe["solicitacao"],
        funcionarios=detalhe["funcionarios"],
        aprovacoes=detalhe["aprovacoes"],
        origem=None,
        print_mode=True,
        provisao=provisao,
        active_menu=None
    )

@bp.route("/solicitacoes/<int:solicitacao_id>/frequencia")
@login_required
def solicitacao_frequencia(solicitacao_id):

    from app.services.solicitacoes_service import (
        obter_frequencia,
        buscar_solicitacao_por_id
    )

    funcionarios = obter_frequencia(solicitacao_id)

    return render_template(
        "solicitacoes-frequencia.html",
        solicitacao_id=solicitacao_id,
        funcionarios=funcionarios,
        active_menu="solicitacoes"
    )

# ==============================
# PWA (root scope)
# ==============================

@bp.route("/offline", endpoint="offline_page")
def offline():
    return render_template("offline.html")

@bp.route("/manifest.webmanifest", endpoint="pwa_manifest")
def manifest():
    from flask import current_app, send_from_directory, make_response
    import os

    static_dir = os.path.join(current_app.root_path, "static")
    resp = make_response(send_from_directory(static_dir, "manifest.webmanifest"))
    resp.headers["Content-Type"] = "application/manifest+json; charset=utf-8"
    resp.headers["Cache-Control"] = "public, max-age=3600"
    return resp
