import click
import pandas as pd
from pathlib import Path
from flask import current_app

from app.extensions import get_db


def normalize_status(value: str) -> str:
    if pd.isna(value):
        return "INACTIVE"

    v = str(value).strip().lower()
    return "ACTIVE" if "ativo" in v else "INACTIVE"


@click.command("import-employees")
def import_employees():
    """Import employees from Excel into PostgreSQL."""

    base_dir = Path(current_app.root_path)
    data_dir = base_dir / "data"

    excel_file = None

    for ext in ("xls", "xlsx", "XLS", "XLSX"):
        candidate = data_dir / f"Lista-de-Funcionarios-Venttos-17-12-25-Completo.{ext}"
        if candidate.exists():
            excel_file = candidate
            break

    if not excel_file:
        raise RuntimeError("Excel file not found inside app/data")

    engine = "xlrd" if excel_file.suffix.lower() == ".xls" else "openpyxl"

    print(f"📊 Reading: {excel_file.name}")

    df = pd.read_excel(excel_file, engine=engine)

    df = df.rename(columns={
        df.columns[1]: "full_name",
        df.columns[2]: "job_title",
        df.columns[3]: "department",
        df.columns[4]: "hired_at",
        df.columns[5]: "status",
        df.columns[6]: "branch_name",
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
    df["hired_at"] = pd.to_datetime(df["hired_at"], errors="coerce").dt.date

    rows = [
        (
            str(r.full_name).strip(),
            r.job_title,
            r.department,
            r.hired_at,
            r.status,
            r.branch_name
        )
        for r in df.itertuples(index=False)
        if r.full_name
    ]

    print(f"📌 Rows to insert: {len(rows)}")

    with get_db() as conn:
        with conn.cursor() as cur:
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
                VALUES (%s,%s,%s,%s,%s,%s)
            """, rows)
        conn.commit()

    print("✅ Employees imported successfully!")
