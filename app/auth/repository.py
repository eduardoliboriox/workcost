from app.extensions import get_db
from psycopg.rows import dict_row
from werkzeug.security import generate_password_hash

# =====================================================
# CORE USERS (Flask-Login / OAuth / Local)
# =====================================================
def get_user_by_id(user_id):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT * FROM users WHERE id=%s",
                (user_id,)
            )
            return cur.fetchone()

def get_user_by_provider(provider, provider_id):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT * FROM users
                WHERE provider=%s AND provider_id=%s
                """,
                (provider, provider_id),
            )
            return cur.fetchone()

def create_user(data):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO users
                (username, email, provider, provider_id, is_active)
                VALUES (%s,%s,%s,%s,TRUE)
                RETURNING *
                """,
                (
                    data["username"],
                    data["email"],
                    data["provider"],
                    data["provider_id"],
                ),
            )
            conn.commit()
            return cur.fetchone()

# =====================================================
# LOCAL AUTH
# =====================================================
def get_user_by_username(username):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT * FROM users WHERE username=%s",
                (username,),
            )
            return cur.fetchone()

def create_local_user(data):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO users
                (username, email, full_name, matricula, setor,
                 password_hash, provider, is_active, is_admin)
                VALUES (%s,%s,%s,%s,%s,%s,'local',%s,%s)
                RETURNING *
                """,
                (
                    data["username"],
                    data["email"],
                    data["full_name"],
                    data["matricula"],
                    data["setor"],
                    data["password_hash"],
                    data["is_active"],
                    data["is_admin"],
                ),
            )
            conn.commit()
            return cur.fetchone()

# =====================================================
# ADMIN
# =====================================================
def list_pending_users(search=None):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            if search:
                cur.execute(
                    """
                    SELECT * FROM users
                    WHERE is_active=FALSE
                      AND provider='local'
                      AND full_name ILIKE %s
                    ORDER BY created_at DESC
                    """,
                    (f"%{search}%",),
                )
            else:
                cur.execute(
                    """
                    SELECT * FROM users
                    WHERE is_active=FALSE
                      AND provider='local'
                    ORDER BY created_at DESC
                    """
                )
            return cur.fetchall()

def approve_user(user_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET is_active=TRUE WHERE id=%s",
                (user_id,),
            )
            conn.commit()

def deny_user(user_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM users WHERE id=%s",
                (user_id,),
            )
            conn.commit()

def count_users():
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT COUNT(*) AS total FROM users")
            row = cur.fetchone()
            return row["total"]

# app/auth/repository.py
def list_all_users(search=None):
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            if search:
                cur.execute(
                    """
                    SELECT * FROM users
                    WHERE full_name ILIKE %s OR username ILIKE %s OR setor ILIKE %s
                    ORDER BY created_at DESC
                    """,
                    (f"%{search}%", f"%{search}%", f"%{search}%")
                )
            else:
                cur.execute(
                    """
                    SELECT * FROM users
                    ORDER BY created_at DESC
                    """
                )
            return cur.fetchall()

# =====================================================
# ALTERAÇÃO DE SENHA
# =====================================================
def update_user_password(user_id: int, new_password: str):
    password_hash = generate_password_hash(new_password)

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET password_hash = %s
                WHERE id = %s
                """,
                (password_hash, user_id),
            )
            conn.commit()

def update_user_role(user_id: int, role: str):
    fields = {
        "admin": ("is_admin", True),
        "extra": ("extra_authorized", True),
        "none": ("is_admin", False, "extra_authorized", False),
    }

    with get_db() as conn:
        with conn.cursor() as cur:
            if role == "admin":
                cur.execute(
                    "UPDATE users SET is_admin=TRUE WHERE id=%s",
                    (user_id,)
                )
            elif role == "extra":
                cur.execute(
                    "UPDATE users SET extra_authorized=TRUE WHERE id=%s",
                    (user_id,)
                )
            else:
                cur.execute(
                    """
                    UPDATE users
                    SET is_admin=FALSE,
                        extra_authorized=FALSE
                    WHERE id=%s
                    """,
                    (user_id,)
                )
        conn.commit()
