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
                    atividades
                )
                VALUES (%s,%s,%s,%s,%s,%s)
                RETURNING id
            """, (
                dados["data"],
                dados["turnos"],
                dados["setores"],
                dados["cliente"],
                dados["descricao"],
                dados["atividades"]
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
