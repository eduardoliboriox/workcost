import psycopg
from psycopg.rows import dict_row
from flask import current_app

def get_db():
    return psycopg.connect(
        current_app.config["DATABASE_URL"],
        row_factory=dict_row,
        sslmode="require"
    )
