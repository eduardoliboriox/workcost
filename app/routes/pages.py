from flask import Blueprint, render_template, request
from app.services.pcp_service import resumo_dashboard
from datetime import date
from app.services import cargos_service

bp = Blueprint("pages", __name__)

@bp.route("/")
def inicio():
    return render_template("inicio.html")

@bp.route("/dashboard")
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
def cargos():
    lista = cargos_service.listar()
    return render_template("cargos.html", cargos=lista)

@bp.route("/lancamento")
def lancamento():
    cargos_tecnica = cargos_service.listar_por_area("TECNICA")
    cargos_producao = cargos_service.listar_por_area("PRODUCAO")

    return render_template(
        "lancamento.html",
        cargos_tecnica=cargos_tecnica,
        cargos_producao=cargos_producao
    )

@bp.route("/dashboard/linha/ferias", methods=["GET"])
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
def relatorios():
    return render_template("relatorios.html", active_menu="dashboard")

@bp.route("/powerbi")
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

    return render_template(
        "powerbi.html",
        filtros=filtros,
        active_menu="dashboard",
        **dados
    )








