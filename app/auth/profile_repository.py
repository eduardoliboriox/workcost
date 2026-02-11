from app.extensions import get_db
from psycopg.rows import dict_row

# ======================================================
# EMPLOYEE LINK
# ======================================================
def find_employee_by_name(full_name: str):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, employee_code
                FROM employees
                WHERE LOWER(full_name) = LOWER(%s)
                LIMIT 1
            """, (full_name,))
            return cur.fetchone()

def link_user_to_employee(user_id: int, employee_id: int):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users
                SET employee_id = %s
                WHERE id = %s
            """, (employee_id, user_id))
        conn.commit()

# ======================================================
# PROFILE
# ======================================================
def get_profile(user_id: int):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT * FROM user_profiles
                WHERE user_id = %s
            """, (user_id,))
            return cur.fetchone()

def upsert_profile(user_id: int, data: dict):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_profiles (
                    user_id, phone, street, number, neighborhood,
                    city, state, zip_code, complement, reference
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    phone=EXCLUDED.phone,
                    street=EXCLUDED.street,
                    number=EXCLUDED.number,
                    neighborhood=EXCLUDED.neighborhood,
                    city=EXCLUDED.city,
                    state=EXCLUDED.state,
                    zip_code=EXCLUDED.zip_code,
                    complement=EXCLUDED.complement,
                    reference=EXCLUDED.reference
            """, (
                user_id,
                data.get("phone"),
                data.get("street"),
                data.get("number"),
                data.get("neighborhood"),
                data.get("city"),
                data.get("state"),
                data.get("zip_code"),
                data.get("complement"),
                data.get("reference"),
            ))
        conn.commit()
