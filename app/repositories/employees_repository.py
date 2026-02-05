from app.extensions import get_db
from psycopg.rows import dict_row


def get_employee_by_matricula(matricula: str):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    e.full_name,
                    p.phone,
                    CONCAT_WS(', ',
                        p.street,
                        p.number,
                        p.neighborhood,
                        p.city,
                        p.state
                    ) AS endereco
                FROM employees e
                LEFT JOIN users u
                  ON (
                       u.employee_id = e.id
                       OR ltrim(u.matricula, '0') = ltrim(e.employee_code, '0')
                     )
                LEFT JOIN user_profiles p
                  ON p.user_id = u.id
                WHERE ltrim(e.employee_code, '0') = ltrim(%s, '0')
                LIMIT 1
            """, (matricula,))

            return cur.fetchone()

