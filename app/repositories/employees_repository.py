from app.extensions import get_db
from psycopg.rows import dict_row


def get_employee_by_matricula(matricula: str):
    """
    Busca funcionário completo para auto-fill da solicitação
    """
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
                LEFT JOIN users u ON u.employee_id = e.id
                LEFT JOIN user_profiles p ON p.user_id = u.id
                WHERE e.employee_code = %s
                LIMIT 1
            """, (matricula,))

            return cur.fetchone()
