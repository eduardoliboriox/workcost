from app.extensions import get_db
from psycopg.rows import dict_row
import json


def inserir_solicitacao(dados: dict, funcionarios: list):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            cur.execute("""
                INSERT INTO solicitacoes (
                    data,
                    turnos,
                    setores,
                    cliente,
                    descricao,
                    atividades,
                    solicitante_user_id
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
            """, (
                dados["data"],
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
                    u.username AS solicitante,
                    s.atividades,
                    COUNT(sa.id) FILTER (WHERE sa.signed_at IS NOT NULL) AS assinadas,
                    COUNT(sa.id) AS total_aprovacoes
                FROM solicitacoes s
                JOIN users u ON u.id = s.solicitante_user_id
                LEFT JOIN solicitacao_aprovacoes sa
                  ON sa.solicitacao_id = s.id
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
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    sf.*,
                    u.username AS signed_by
                FROM solicitacao_funcionarios sf
                LEFT JOIN users u
                  ON ltrim(u.matricula, '0') = ltrim(sf.matricula, '0')
                WHERE sf.solicitacao_id = %s
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


def registrar_aprovacao(
    solicitacao_id: int,
    user_id: int,
    role: str
):
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

