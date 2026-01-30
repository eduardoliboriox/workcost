from app.extensions import get_db
from psycopg.rows import dict_row

def listar():
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, setor, linha, hc_padrao
                FROM hc_linhas
                ORDER BY setor, linha
            """)
            return cur.fetchall()

def inserir(setor, linha, hc_padrao):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO hc_linhas (setor, linha, hc_padrao)
                VALUES (%s, %s, %s)
                ON CONFLICT (setor, linha)
                DO UPDATE SET hc_padrao = EXCLUDED.hc_padrao
            """, (setor, linha, hc_padrao))
        conn.commit()

def excluir(id_):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM hc_linhas WHERE id = %s", (id_,))
        conn.commit()
