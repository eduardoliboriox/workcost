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


