from app.repositories.employees_repository import get_employee_by_matricula


def buscar_funcionario(matricula: str):
    funcionario = get_employee_by_matricula(matricula)

    if not funcionario:
        return {"found": False}

    return {
        "found": True,
        "nome": funcionario["full_name"],
        "telefone": funcionario["phone"],
        "endereco": funcionario["endereco"]
    }
