from flask import Blueprint, render_template, request
from app.services.pcp_service import resumo_dashboard

bp = Blueprint("pages", __name__)

@bp.route("/")
@bp.route("/dashboard")
def dashboard():
    filtros = {
        "data": request.args.get("data"),
        "turno": request.args.get("turno"),
        "filial": request.args.get("filial")
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
