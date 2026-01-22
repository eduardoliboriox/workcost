from flask import Blueprint, request, jsonify
from app.services import modelos_service, cargos_service
from app.services.lancamentos_service import criar_lancamento, cargos_faltas_por_linha

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

@bp.route("/cargos", methods=["GET"])
def listar_cargos():
    return jsonify(cargos_service.listar())

@bp.route("/cargos", methods=["POST"])
def cadastrar_cargo():
    return jsonify(cargos_service.cadastrar(request.form))

@bp.route("/cargos", methods=["PUT"])
def atualizar_cargo():
    return jsonify(cargos_service.atualizar(request.form))

@bp.route("/cargos", methods=["DELETE"])
def excluir_cargo():
    return jsonify(cargos_service.excluir(request.form))

@bp.route("/dashboard/linha/cargos", methods=["GET"])
def cargos_por_linha_api():
    linha = request.args.get("linha")

    filtros = {
        "data_inicial": request.args.get("data_inicial"),
        "data_final": request.args.get("data_final"),
        "turno": request.args.get("turno"),
        "filial": request.args.get("filial")
    }

    return jsonify(cargos_faltas_por_linha(linha, filtros))

