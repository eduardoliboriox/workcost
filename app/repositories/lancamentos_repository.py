from app.extensions import get_db

def inserir(d):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO lancamentos (
                    data, filial, setor, turno, linha,
                    cliente, hc_padrao, hc_real, ferias, absenteismo
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                d["data"],
                d["filial"],
                d["setor"],
                d["turno"],
                d["linha"],
                d.get("cliente"),
                d["hc_padrao"],
                d["hc_real"],
                d.get("ferias", 0),
                d["absenteismo"]
            ))
        conn.commit()
