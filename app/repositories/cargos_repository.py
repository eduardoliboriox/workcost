from app.extensions import get_db

def listar():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cargos ORDER BY nome")
            return cur.fetchall()

def inserir(nome):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO cargos (nome) VALUES (%s)",
                (nome,)
            )
        conn.commit()

def excluir(id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM cargos WHERE id = %s", (id,))
        conn.commit()
