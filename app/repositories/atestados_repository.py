from app.extensions import get_db

def inserir(data, matricula, cargo_id, tipo):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO lancamentos_atestados
                (data, matricula, cargo_id, tipo)
                VALUES (%s, %s, %s, %s)
            """, (data, matricula, cargo_id, tipo))
        conn.commit()
