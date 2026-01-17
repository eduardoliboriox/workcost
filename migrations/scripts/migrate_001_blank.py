import os
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definida")

with psycopg.connect(DATABASE_URL, sslmode="require") as conn:
    with conn.cursor() as cur:
        cur.execute("""
            ALTER TABLE modelos
            ADD COLUMN IF NOT EXISTS blank INTEGER NOT NULL DEFAULT 1;
        """)
    conn.commit()

print("✅ Coluna 'blank' criada com sucesso")

