from app.extensions import get_db
from psycopg.rows import dict_row

def inserir_com_cargos(d, cargos):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                INSERT INTO lancamentos (
                    data, filial, setor, turno, linha,
                    cliente, hc_padrao, hc_real, ferias, absenteismo
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
            """, (
                d["data"], d["filial"], d["setor"], d["turno"], d["linha"],
                d.get("cliente"), d["hc_padrao"], d["hc_real"], 0, d["absenteismo"]
            ))
            lancamento_id = cur.fetchone()["id"]

            for c in cargos:
                cur.execute("""
                    INSERT INTO lancamentos_cargos
                    (lancamento_id, cargo_id, quantidade, tipo)
                    VALUES (%s,%s,%s,%s)
                """, (
                    lancamento_id, c["cargo_id"], c["quantidade"], c["tipo"]
                ))

        conn.commit()

def ferias_cargos_por_linha(linha, filtros):
    from app.extensions import get_db
    where = ["l.linha = %s", "lc.tipo = 'FERIAS'"]
    params = [linha]

    if filtros.get("data_inicial") and filtros.get("data_final"):
        where.append("l.data BETWEEN %s AND %s")
        params += [filtros["data_inicial"], filtros["data_final"]]

    if filtros.get("turno"):
        where.append("l.turno = %s")
        params.append(filtros["turno"])

    if filtros.get("filial"):
        where.append("l.filial = %s")
        params.append(filtros["filial"])

    query = f"""
        SELECT c.nome, SUM(lc.quantidade) AS total
        FROM lancamentos_cargos lc
        JOIN cargos c ON c.id = lc.cargo_id
        JOIN lancamentos l ON l.id = lc.lancamento_id
        WHERE {" AND ".join(where)}
        GROUP BY c.nome
        ORDER BY total DESC
    """

    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, params)
            return cur.fetchall()
