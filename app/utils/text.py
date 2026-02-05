import unicodedata
import re


def normalize_username(value: str) -> str:
    """
    Normaliza string para uso como username:
    - remove acentos
    - converte para lowercase
    - remove caracteres inválidos
    - mantém letras, números e ponto
    """
    if not value:
        return ""

    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9.]", "", value)

    return value
