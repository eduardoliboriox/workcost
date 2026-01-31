import os
from pathlib import Path
import pandas as pd
import psycopg

DATABASE_URL = os.environ["DATABASE_URL"]

BASE_DIR = Path(__file__).resolve().parents[2]
EXCEL_PATH = BASE_DIR / "data" / "Lista de Funcionarios Venttos 17.12.25 - Completo.XLS"

def normalize_status(value):
    if not value or pd.isna(value):
        return "INACTIVE"
    return "ACTIVE" if "ativo" in str(value).lower() else "INACTIVE"

def main():
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

    with psycopg.connect(
        DATABASE_URL,
        sslmode="require",
        connect_timeout=10
    ) as conn:
        with conn.cursor() as cur:
            cur.executemany("""
                INSERT INTO employees
                (full_name, job_title, department, hired_at, status, branch_name)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, data)

        conn.commit()

    print(f"✅ Imported {len(data)} employees")

if __name__ == "__main__":
    main()
