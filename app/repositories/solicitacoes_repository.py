from app.extensions import get_db
from datetime import date
from psycopg.rows import dict_row
import json


def inserir_solicitacao(dados: dict, funcionarios: list):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            cur.execute("""
                INSERT INTO solicitacoes (
                    data,
                    data_execucao,
                    turnos,
                    setores,
                    cliente,
                    descricao,
                    atividades,
                    solicitante_user_id
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
            """, (
                dados["data"],
                dados.get("data_execucao"),
                dados["turnos"],
                dados["setores"],
                dados["cliente"],
                dados["descricao"],
                dados["atividades"],
                dados["solicitante_user_id"]
            ))

            solicitacao_id = cur.fetchone()["id"]

            for f in funcionarios:
                cur.execute("""
                    INSERT INTO solicitacao_funcionarios (
                        solicitacao_id,
                        matricula,
                        nome,
                        endereco,
                        telefone,
                        inicio,
                        termino,
                        transporte
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    solicitacao_id,
                    f["matricula"],
                    f["nome"],
                    f["endereco"],
                    f["telefone"],
                    f["inicio"],
                    f["termino"],
                    f["transporte"]
                ))

        conn.commit()


def listar_solicitacoes_abertas():
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    s.id,
                    s.data,
                    s.data_execucao,
                    u.username AS solicitante,
                    s.atividades,
                    COUNT(sf.id) FILTER (WHERE sf.signed_at IS NOT NULL) AS assinadas,
                    COUNT(sf.id) AS total_funcionarios
                FROM solicitacoes s
                JOIN users u ON u.id = s.solicitante_user_id
                LEFT JOIN solicitacao_funcionarios sf
                  ON sf.solicitacao_id = s.id
                GROUP BY s.id, u.username
                ORDER BY s.id DESC
            """)
            return cur.fetchall()


def listar_aprovacoes_por_solicitacao():
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    sa.solicitacao_id,
                    sa.role,
                    u.username,
                    sa.signed_at
                FROM solicitacao_aprovacoes sa
                JOIN users u ON u.id = sa.user_id
            """)
            return cur.fetchall()


def buscar_solicitacao_por_id(solicitacao_id: int):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    s.*,
                    u.username AS solicitante
                FROM solicitacoes s
                JOIN users u ON u.id = s.solicitante_user_id
                WHERE s.id = %s
            """, (solicitacao_id,))
            return cur.fetchone()


def listar_funcionarios_por_solicitacao(solicitacao_id: int):
    """
    REGRA:
    - funcionário só está confirmado se signed_at IS NOT NULL
    - NÃO inferir confirmação via tabela users
    """
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    sf.*
                FROM solicitacao_funcionarios sf
                WHERE sf.solicitacao_id = %s
                ORDER BY sf.id
            """, (solicitacao_id,))
            return cur.fetchall()


def listar_aprovacoes_por_solicitacao_id(solicitacao_id: int):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    sa.role,
                    sa.signed_at,
                    u.username
                FROM solicitacao_aprovacoes sa
                JOIN users u ON u.id = sa.user_id
                WHERE sa.solicitacao_id = %s
            """, (solicitacao_id,))
            return cur.fetchall()


def registrar_aprovacao(solicitacao_id: int, user_id: int, role: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO solicitacao_aprovacoes (
                    solicitacao_id,
                    user_id,
                    role,
                    signed_at
                )
                VALUES (%s,%s,%s, now())
                ON CONFLICT (solicitacao_id, role)
                DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    signed_at = now()
            """, (solicitacao_id, user_id, role))
        conn.commit()


def registrar_assinatura_funcionario(
    solicitacao_id: int,
    matricula: str,
    username: str
):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE solicitacao_funcionarios
                SET signed_at = now(),
                    signed_by = %s
                WHERE solicitacao_id = %s
                  AND ltrim(matricula, '0') = ltrim(%s, '0')
            """, (username, solicitacao_id, matricula))
        conn.commit()


def listar_solicitacoes_abertas_por_matricula(matricula: str):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT DISTINCT
                    s.id,
                    s.data,
                    s.data_execucao,
                    u.username AS solicitante,
                    s.atividades,
                    COUNT(sf.id) FILTER (WHERE sf.signed_at IS NOT NULL) AS assinadas,
                    COUNT(sf.id) AS total_funcionarios
                FROM solicitacoes s
                JOIN users u ON u.id = s.solicitante_user_id
                JOIN solicitacao_funcionarios sf
                  ON sf.solicitacao_id = s.id
                WHERE ltrim(sf.matricula, '0') = ltrim(%s, '0')
                GROUP BY s.id, u.username
                ORDER BY s.id DESC
            """, (matricula,))
            return cur.fetchall()


def atualizar_recebido_em(solicitacao_id: int, recebido_em: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE solicitacoes
                SET recebido_em = %s
                WHERE id = %s
            """, (recebido_em, solicitacao_id))
        conn.commit()


def atualizar_lancado_em(solicitacao_id: int, lancado_em: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE solicitacoes
                SET lancado_em = %s
                WHERE id = %s
            """, (lancado_em, solicitacao_id))
        conn.commit()


def deletar_solicitacao_por_id(solicitacao_id: int):
    """
    Remove completamente uma solicitação do banco.
    Ordem:
    1. solicitacao_aprovacoes
    2. solicitacao_funcionarios
    3. solicitacoes
    """

    with get_db() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                DELETE FROM solicitacao_aprovacoes
                WHERE solicitacao_id = %s
            """, (solicitacao_id,))

            cur.execute("""
                DELETE FROM solicitacao_funcionarios
                WHERE solicitacao_id = %s
            """, (solicitacao_id,))

            cur.execute("""
                DELETE FROM solicitacoes
                WHERE id = %s
            """, (solicitacao_id,))

        conn.commit()


def listar_solicitacoes_com_status():
    """
    Retorna todas as solicitações com contagem de assinaturas.
    Service decide se é aberta ou fechada.
    """

    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    s.id,
                    s.data,
                    s.data_execucao,
                    s.objetivo_status,
                    s.observacoes,
                    u.username AS solicitante,
                    s.atividades,
                    COUNT(sf.id) FILTER (WHERE sf.signed_at IS NOT NULL) AS assinadas,
                    COUNT(sf.id) AS total_funcionarios
                FROM solicitacoes s
                JOIN users u ON u.id = s.solicitante_user_id
                LEFT JOIN solicitacao_funcionarios sf
                  ON sf.solicitacao_id = s.id
                GROUP BY 
                    s.id,
                    s.data,
                    s.data_execucao,
                    s.objetivo_status,
                    s.observacoes,
                    u.username,
                    s.atividades
                ORDER BY s.id DESC
            """)
            return cur.fetchall()

def listar_frequencia_por_solicitacao(solicitacao_id: int):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT matricula, compareceu
                FROM solicitacao_frequencia
                WHERE solicitacao_id = %s
            """, (solicitacao_id,))
            return cur.fetchall()


def salvar_frequencia(
    solicitacao_id: int,
    matricula: str,
    compareceu: bool
):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO solicitacao_frequencia (
                    solicitacao_id,
                    matricula,
                    compareceu
                )
                VALUES (%s,%s,%s)
                ON CONFLICT (solicitacao_id, matricula)
                DO UPDATE SET compareceu = EXCLUDED.compareceu
            """, (solicitacao_id, matricula, compareceu))
        conn.commit()


def contar_presencas(solicitacao_id: int):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT COUNT(*) AS total
                FROM solicitacao_frequencia
                WHERE solicitacao_id = %s
                  AND compareceu = TRUE
            """, (solicitacao_id,))
            return cur.fetchone()["total"]

def atualizar_fechamento(
    solicitacao_id: int,
    objetivo_status: str,
    observacoes: str
):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE solicitacoes
                SET objetivo_status = %s,
                    observacoes = %s
                WHERE id = %s
            """, (objetivo_status, observacoes, solicitacao_id))
        conn.commit()


def listar_extras_com_provisao():
    """
    Retorna todas as solicitações com:
    - filial (cliente)
    - data_execucao
    - turnos
    - total provisão calculado
    """

    from app.services.provisao_service import gerar_provisao

    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            cur.execute("""
                SELECT
                    s.id,
                    s.cliente,
                    s.data_execucao,
                    s.turnos
                FROM solicitacoes s
                ORDER BY s.id DESC
            """)

            solicitacoes = cur.fetchall()

    resultado = []

    for s in solicitacoes:

        funcionarios = listar_funcionarios_por_solicitacao(s["id"])

        provisao = gerar_provisao(s, funcionarios)

        resultado.append({
            "filial": s["cliente"],
            "data_execucao": s["data_execucao"],
            "turnos": s["turnos"],  
            "total_provisao": provisao["total_geral"]
        })

    return resultado
