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
