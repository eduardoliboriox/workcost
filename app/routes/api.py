from flask import Blueprint, request, jsonify
from app.services import modelos_service
from app.services.lancamentos_service import criar_lancamento

bp = Blueprint("api", __name__)

@bp.route("/modelos", methods=["GET"])
def listar():
    return jsonify(modelos_service.listar_modelos())

@bp.route("/modelos", methods=["POST"])
def cadastrar():
    return jsonify(modelos_service.cadastrar_modelo(request.form))

@bp.route("/modelos", methods=["DELETE"])
def excluir():
    return jsonify(modelos_service.excluir_modelo(request.form))

@bp.route("/lancamentos", methods=["POST"])
def api_criar_lancamento():
    dados = request.form
    return jsonify(criar_lancamento(dados))

