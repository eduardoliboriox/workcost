from flask import Blueprint, render_template
from app.services.pcp_service import resumo_dashboard

bp = Blueprint("pages", __name__)

@bp.route("/")
@bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", **resumo_dashboard())

@bp.route("/lancamento")
def lancamento():
    return render_template("lancamento.html", codigos=[])

@bp.route("/modelos")
def modelos():
    return render_template("modelos.html", modelos=[])

@bp.route("/calculo")
def calculo():
    return render_template("calcular.html")
