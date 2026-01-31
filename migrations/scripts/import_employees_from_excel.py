import os
from pathlib import Path
import pandas as pd
import psycopg


# =========================
# CONFIG
# =========================
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

BASE_DIR = Path(__file__).resolve().parents[2]
EXCEL_PATH = (
    BASE_DIR
    / "app"
    / "data"
    / "Lista de Funcionarios Venttos 17.12.25 - Completo.xls"
)

if not EXCEL_PATH.exists():
    raise FileNotFoundError(f"Excel not found: {EXCEL_PATH}")


# =========================
# HELPERS
# =========================
def normalize_status(value) -> str:
    if pd.isna(value):
        return "INACTIVE"
    v = str(value).lower()
    return "ACTIVE" if "ativo" in v else "INACTIVE"


# =========================
# MAIN
# =========================
def main():
    print("📊 Reading Excel...")

    df = pd.read_excel(
        EXCEL_PATH,
        engine="openpyxl"  # ✔️ funciona
    )

    df = df.rename(columns={
        df.columns[1]: "full_name",        # Coluna B
        df.columns[2]: "job_title",        # Coluna C
        df.columns[3]: "department",       # Coluna D
        df.columns[4]: "hired_at",         # Coluna E
        df.columns[5]: "status",            # Coluna F
        df.columns[6]: "branch_name",       # Coluna G
    })

    df = df[[
        "full_name",
        "job_title",
        "department",
        "hired_at",
        "status",
        "branch_name"
    ]]

    df["status"] = df["status"].apply(normalize_status)
    df["hired_at"] = pd.to_datetime(
        df["hired_at"],
        errors="coerce"
    ).dt.date

    rows = [
        (
            r.full_name.strip(),
            r.job_title,
            r.department,
            r.hired_at,
            r.status,
            r.branch_name
        )
        for r in df.itertuples(index=False)
        if r.full_name
    ]

    print(f"🚀 Importing {len(rows)} employees...")

    with psycopg.connect(
        DATABASE_URL,
        sslmode="require",
        connect_timeout=15
    ) as conn:
        with conn.cursor() as cur:

            # Evita duplicação
            cur.execute("TRUNCATE TABLE employees RESTART IDENTITY;")

            cur.executemany("""
                INSERT INTO employees (
                    full_name,
                    job_title,
                    department,
                    hired_at,
                    status,
                    branch_name
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, rows)

        conn.commit()

    print("✅ Employees imported successfully")


if __name__ == "__main__":
    main()
