import os

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    # 🔐 Senhas operacionais
    SENHA_ATESTADO = os.getenv("SENHA_ATESTADO", "1234")
    SENHA_ABONO = os.getenv("SENHA_ABONO", "5678")
