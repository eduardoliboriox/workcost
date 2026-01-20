from flask import Blueprint, render_template, request
from app.services.pcp_service import resumo_dashboard
from datetime import date

bp = Blueprint("pages", __name__)

@bp.route("/")
@bp.route("/dashboard")
def dashboard():
    # filtro de datas
    data_inicial = request.args.get("data_inicial")
    data_final = request.args.get("data_final")
    turno = request.args.get("turno")
    filial = request.args.get("filial")

    # se não informar, default = hoje
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


@bp.route("/lancamento")
def lancamento():
    return render_template("lancamento.html", codigos=[])

@bp.route("/modelos")
def modelos():
    return render_template("modelos.html", modelos=[])

@bp.route("/calculo")
def calculo():
    return render_template("calcular.html")
