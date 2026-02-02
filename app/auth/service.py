from werkzeug.security import generate_password_hash, check_password_hash

# users core
from app.auth.repository import (
    get_user_by_provider,
    create_user,
    create_local_user,
    get_user_by_username,
    count_users,
    get_user_by_id,
    update_user_password,
    get_user_by_matricula
)

# profile / employee link
from app.auth.profile_repository import (
    find_employee_by_name,
    link_user_to_employee,
    upsert_profile,
)


# =====================================================
# OAUTH
# =====================================================
def get_or_create_user(profile, provider):
    provider_id = profile["id"]
    email = profile["email"]
    username = email.split("@")[0]

    user = get_user_by_provider(provider, provider_id)
    if user:
        return user

    return create_user({
        "username": username,
        "email": email,
        "provider": provider,
        "provider_id": provider_id
    })


# =====================================================
# REGISTER
# =====================================================
def generate_username(full_name: str) -> str:
    parts = full_name.strip().lower().split()
    return f"{parts[0]}.{parts[-1]}"


def register_user(form):
    if form["password"] != form["password_confirm"]:
        raise ValueError("As senhas não conferem")

    username = generate_username(form["full_name"])

    password_hash = generate_password_hash(form["password"])

    is_first_user = count_users() == 0

    return create_local_user({
        "username": username,
        "email": form["email"],
        "full_name": form["full_name"],
        "matricula": form["matricula"],
        "setor": form["setor"],
        "password_hash": password_hash,
        "is_active": is_first_user,
        "is_admin": is_first_user
    })


# =====================================================
# LOGIN LOCAL
# =====================================================
def authenticate_local(username, password):
    user = get_user_by_username(username)

    if not user:
        return None

    if not user["is_active"]:
        return "PENDING"

    if not check_password_hash(user["password_hash"], password):
        return None

    return user


# =====================================================
# PASSWORD
# =====================================================
def change_user_password(user_id, current_password, new_password, confirm_password):
    if not new_password:
        return "EMPTY"

    if new_password != confirm_password:
        raise ValueError("Nova senha e confirmação não conferem")

    user = get_user_by_id(user_id)

    if not check_password_hash(user["password_hash"], current_password):
        raise ValueError("Senha atual incorreta")

    update_user_password(user_id, new_password)

    return "OK"


# =====================================================
# PROFILE + EMPLOYEE LINK
# =====================================================
def attach_employee_and_profile(user_id: int, form):
    """
    - link user to employee by full_name
    - save contact/address profile
    """

    employee = find_employee_by_name(form["full_name"])

    if employee:
        link_user_to_employee(user_id, employee["id"])

    upsert_profile(user_id, form)



def confirm_employee_extra(matricula: str, password: str):
    # Blindagem de entrada
    matricula = matricula.strip()

    user = get_user_by_matricula(matricula)

    if not user:
        return {"success": False, "error": "Usuário não encontrado"}

    if not user["is_active"]:
        return {"success": False, "error": "Usuário inativo"}

    if not check_password_hash(user["password_hash"], password):
        return {"success": False, "error": "Senha inválida"}

    return {
        "success": True,
        "username": user["username"]
    }
