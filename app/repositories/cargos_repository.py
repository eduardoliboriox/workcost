from app.extensions import get_db

def listar():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, nome, area
                FROM cargos
                ORDER BY area, nome
            """)
            return cur.fetchall()

def listar_por_area(area):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, nome
                FROM cargos
                WHERE area = %s
                ORDER BY nome
            """, (area,))
            return cur.fetchall()

def inserir(nome, area):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO cargos (nome, area)
                VALUES (%s, %s)
            """, (nome, area))
        conn.commit()

def atualizar(id, nome, area):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE cargos
                SET nome = %s,
                    area = %s
                WHERE id = %s
            """, (nome, area, id))
        conn.commit()

def excluir(id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM cargos WHERE id = %s", (id,))
        conn.commit()
