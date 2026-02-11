from flask import Blueprint, request, jsonify
from app.services import modelos_service, cargos_service
from app.services.lancamentos_service import (
    criar_lancamento,
    faltas_por_linha,
    ferias_por_linha_cargos
)
from app.services.pcp_service import ranking_linhas_ferias
from app.services.relatorios_service import gerar_relatorio
from app.services import hc_linhas_service
from app.services.solicitacoes_service import criar_solicitacao
from app.services.employees_service import buscar_funcionario
from app.auth.service import confirm_employee_extra

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

@bp.route("/lancamentos", methods=["POST"])
def api_criar_lancamento():
    dados = request.form
    resultado = criar_lancamento(dados)
    status_code = 200 if resultado.get("success") else 400
    return jsonify(resultado), status_code

@bp.route("/dashboard/linhas/ferias", methods=["GET"])
def api_ranking_linhas_ferias():
    filtros = {
        "data_inicial": request.args.get("data_inicial"),
        "data_final": request.args.get("data_final"),
        "turno": request.args.get("turno"),
        "filial": request.args.get("filial")
    }
    return jsonify(ranking_linhas_ferias(filtros))

@bp.route("/dashboard/linha/cargos", methods=["GET"])
def api_faltas_linha():
    filtros = {
        "data_inicial": request.args.get("data_inicial"),
        "data_final": request.args.get("data_final"),
        "turno": request.args.get("turno"),
        "filial": request.args.get("filial")
    }
    linha = request.args.get("linha")
    return jsonify(faltas_por_linha(linha, filtros))

@bp.route("/dashboard/linha/ferias_cargos", methods=["GET"])
def api_ferias_linha_cargos():
    filtros = {
        "data_inicial": request.args.get("data_inicial"),
        "data_final": request.args.get("data_final"),
        "turno": request.args.get("turno"),
        "filial": request.args.get("filial")
    }
    linha = request.args.get("linha")
    return jsonify(ferias_por_linha_cargos(linha, filtros))

@bp.route("/linhas", methods=["GET"])
def api_linhas_por_setor():
    setor = request.args.get("setor")
    linhas = {
        "IM": ["IM-01", "IM-02"],
        "PA": ["PA-01", "PA-02"],
        "SMT": ["SMT-01", "SMT-02"],
        "PTH": ["PTH-01"],
        "VTT": ["VTT-01"]
    }
    if not setor or setor == "Todos":
        return jsonify([])
    return jsonify(linhas.get(setor, []))

@bp.route("/relatorios", methods=["GET"])
def api_relatorios():
    setor = request.args.get("setor") or None
    tipo = request.args.get("tipo", "MENSAL")

    dados = gerar_relatorio(setor, tipo)
    return jsonify(dados)

@bp.route("/hc-linhas", methods=["GET"])
def api_listar_hc_linhas():
    return jsonify(hc_linhas_service.listar())

@bp.route("/hc-linhas", methods=["POST"])
def api_salvar_hc_linha():
    return jsonify(hc_linhas_service.salvar(request.form))

@bp.route("/hc-linhas", methods=["DELETE"])
def api_excluir_hc_linha():
    return jsonify(
        hc_linhas_service.excluir(request.form.get("id"))
    )

@bp.route("/powerbi/resumo", methods=["GET"])
def api_powerbi_resumo():
    filtros = {
        "data_inicial": request.args.get("data_inicial"),
        "data_final": request.args.get("data_final"),
        "turno": request.args.get("turno"),
        "filial": request.args.get("filial"),
        "setor": request.args.get("setor"),
        "linha": request.args.get("linha"),
    }

    from app.services.pcp_service import (
        resumo_dashboard,
        ranking_linhas_faltas_powerbi
    )

    resumo = resumo_dashboard(filtros)

    return jsonify({
        "kpis": resumo["kpis"],
        "ranking_faltas": ranking_linhas_faltas_powerbi(filtros)
    })

@bp.route("/dashboard/resumo", methods=["GET"])
def api_dashboard_resumo():
    filtros = {
        "data_inicial": request.args.get("data_inicial"),
        "data_final": request.args.get("data_final"),
        "turno": request.args.get("turno"),
        "filial": request.args.get("filial")
    }

    from app.services.pcp_service import resumo_dashboard

    dados = resumo_dashboard(filtros)

    return jsonify({
        "kpis": dados["kpis"],
        "ranking_setor": dados["ranking_setor"],
        "ranking_filial": dados["ranking_filial"],
        "ranking_linhas": dados["ranking_linhas"],
        "ranking_linhas_ferias": dados["ranking_linhas_ferias"],
        "ranking_cargos": dados["ranking_cargos"]
    })


@bp.route("/solicitacoes", methods=["POST"])
def api_criar_solicitacao():
    result = criar_solicitacao(request.form)
    return jsonify(result), (200 if result["success"] else 400)

@bp.route("/employees/<matricula>", methods=["GET"])
def api_employee_lookup(matricula):
    return jsonify(buscar_funcionario(matricula))

@bp.route("/auth/confirm-extra", methods=["POST"])
def api_confirm_extra():
    data = request.get_json() or {}

    matricula = data.get("matricula")
    password = data.get("password")

    if not matricula or not password:
        return jsonify({
            "success": False,
            "error": "Dados incompletos"
        }), 400

    result = confirm_employee_extra(matricula, password)
    return jsonify(result), (200 if result["success"] else 401)

@bp.route("/solicitacoes/<int:solicitacao_id>/aprovar", methods=["POST"])
def api_aprovar_solicitacao(solicitacao_id):
    data = request.get_json() or {}
    role = data.get("role")

    if not role:
        return jsonify({"success": False}), 400

    from app.services.solicitacoes_service import aprovar_solicitacao

    aprovar_solicitacao(solicitacao_id, role)
    return jsonify({"success": True})

@bp.route("/solicitacoes/<int:solicitacao_id>/provisao", methods=["GET"])
def api_provisao_gastos_extra(solicitacao_id):
    from app.services.relatorios_service import gerar_provisao_gastos_extra
    return jsonify(gerar_provisao_gastos_extra(solicitacao_id))

@bp.route(
    "/solicitacoes/<int:solicitacao_id>/confirmar-presenca",
    methods=["POST"]
)
def api_confirmar_presenca_funcionario(solicitacao_id):
    data = request.get_json() or {}

    matricula = data.get("matricula")
    password = data.get("password")

    if not matricula or not password:
        return jsonify({
            "success": False,
            "error": "Dados incompletos"
        }), 400

    from app.services.solicitacoes_service import (
        confirmar_presenca_funcionario
    )

    result = confirmar_presenca_funcionario(
        solicitacao_id,
        matricula,
        password
    )

    return jsonify(result), (200 if result["success"] else 401)

@bp.route(
    "/solicitacoes/<int:solicitacao_id>/salvar-view",
    methods=["POST"]
)
def api_salvar_view_solicitacao(solicitacao_id):
    data = request.get_json() or {}

    from app.services.solicitacoes_service import salvar_view_solicitacao

    salvar_view_solicitacao(
        solicitacao_id=solicitacao_id,
        aprovacoes=data.get("aprovacoes", []),
        funcionarios=data.get("funcionarios", []),
        recebido_em=data.get("recebido_em"),
        lancado_em=data.get("lancado_em")
    )

    return jsonify({"success": True})
