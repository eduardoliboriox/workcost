import os
from pathlib import Path
import pandas as pd
import psycopg

# =========================
# CONFIG
# =========================
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

BASE_DIR = Path(__file__).resolve().parents[2]
EXCEL_PATH = BASE_DIR / "app" / "data" / "Lista de Funcionarios Venttos 17.12.25 - Completo.XLS"

if not EXCEL_PATH.exists():
    raise FileNotFoundError(f"Excel not found: {EXCEL_PATH}")

# =========================
# HELPERS
# =========================
def normalize_status(value: str) -> str:
    if not value or pd.isna(value):
        return "INACTIVE"
    return "ACTIVE" if "ativo" in str(value).lower() else "INACTIVE"

# =========================
# MAIN
# =========================
def main():
    print("📊 Reading Excel...")

    df = pd.read_excel(EXCEL_PATH, engine="xlrd")

    df = df.rename(columns={
        "Nome": "full_name",
        "Nome Funcão": "job_title",
        "Descrição Seção": "department",
        "Data de Admissão": "hired_at",
        "Descrição da Situação": "status",
        "Nome da Filial": "branch_name",
    })

    df["status"] = df["status"].apply(normalize_status)
    df["hired_at"] = pd.to_datetime(
        df["hired_at"],
        format="%d/%m/%Y",
        errors="coerce"
    ).dt.date

    data = [
        (
            r.full_name,
            r.job_title,
            r.department,
            r.hired_at,
            r.status,
            r.branch_name
        )
        for r in df.itertuples(index=False)
    ]

    print(f"🚀 Importing {len(data)} employees...")

    with psycopg.connect(
        DATABASE_URL,
        sslmode="require",
        connect_timeout=15
    ) as conn:
        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id SERIAL PRIMARY KEY,
                    full_name VARCHAR(150) NOT NULL,
                    job_title VARCHAR(150),
                    department VARCHAR(150),
                    hired_at DATE,
                    status VARCHAR(20),
                    branch_name VARCHAR(150),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)

            cur.executemany("""
                INSERT INTO employees
                (full_name, job_title, department, hired_at, status, branch_name)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, data)

        conn.commit()

    print("✅ Employees imported successfully")

if __name__ == "__main__":
    main()
