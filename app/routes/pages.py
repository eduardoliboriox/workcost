from flask import Blueprint, render_template
from app.services.modelos_service import resumo_dashboard

bp = Blueprint("pages", __name__)

@bp.route("/")
@bp.route("/dashboard")
def dashboard():
    dados = resumo_dashboard()
    return render_template("dashboard.html", **dados)

@bp.route("/cadastro")
def cadastro():
    return render_template("lancamento.html", codigos=[])

@bp.route("/modelos")
def modelos():
    return render_template("modelos.html", modelos=[])

@bp.route("/calculo")
def calculo():
    return render_template("calcular.html")
