from app.repositories.employees_repository import (
    get_employee_by_code,
    get_employee_by_matricula
)
from app.auth.repository import get_user_by_matricula
from app.auth.profile_repository import get_profile


def buscar_funcionario(matricula: str):
    """
    Autofill de funcionário (modo CREATE).

    Regra:
    1. Busca dados base em employees
    2. Se endereço/telefone estiver vazio,
       complementa com user_profiles
    """

    matricula = matricula.strip().lstrip("0")

    employee = get_employee_by_code(matricula)

    if not employee:
        return {"found": False}

    nome = employee.get("full_name")
    endereco = employee.get("address")
    telefone = employee.get("phone")

    # 🔁 Fallback: user_profiles
    if not endereco or not telefone:
        user = get_user_by_matricula(matricula)
        if user:
            profile = get_profile(user["id"])
            if profile:
                telefone = telefone or profile.get("phone")

                endereco = endereco or ", ".join(filter(None, [
                    profile.get("street"),
                    profile.get("number"),
                    profile.get("neighborhood"),
                    f'{profile.get("city")}/{profile.get("state")}'
                    if profile.get("city") and profile.get("state") else None
                ]))

    return {
        "found": True,
        "nome": nome,
        "endereco": endereco,
        "telefone": telefone
    }
