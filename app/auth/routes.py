from flask import Blueprint, redirect, url_for, render_template, current_app, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from app.auth.service import get_or_create_user, register_user, authenticate_local
from app.auth.models import User
from app.auth.repository import list_pending_users, approve_user, deny_user, list_all_users
from app.auth.decorators import admin_required
from user_agents import parse


bp = Blueprint("auth", __name__)
oauth = OAuth()

@bp.record_once
def setup_oauth(state):
    app = state.app
    oauth.init_app(app)

    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    oauth.register(
        name="github",
        client_id=app.config["GITHUB_CLIENT_ID"],
        client_secret=app.config["GITHUB_CLIENT_SECRET"],
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )

@bp.route("/login")
def login():
    user_agent = parse(request.headers.get("User-Agent", ""))

    # Mobile (celular)
    if user_agent.is_mobile:
        return redirect(url_for("auth.login_mobile_choice"))

    # Desktop
    return render_template("auth/login.html")


@bp.route("/login/google")
def login_google():
    return oauth.google.authorize_redirect(
        url_for("auth.google_callback", _external=True)
    )

@bp.route("/auth/google")
def google_callback():
    token = oauth.google.authorize_access_token()
    userinfo = oauth.google.parse_id_token(token)

    user_data = get_or_create_user(userinfo, "google")
    login_user(User(user_data))

    return redirect(url_for("pages.dashboard"))

@bp.route("/login/github")
def login_github():
    return oauth.github.authorize_redirect(
        url_for("auth.github_callback", _external=True)
    )

@bp.route("/auth/github")
def github_callback():
    token = oauth.github.authorize_access_token()
    resp = oauth.github.get("user")
    profile = resp.json()

    # email no GitHub pode vir separado
    if not profile.get("email"):
        emails = oauth.github.get("user/emails").json()
        primary = next(e for e in emails if e["primary"])
        profile["email"] = primary["email"]

    user_data = get_or_create_user(profile, "github")
    login_user(User(user_data))

    return redirect(url_for("pages.dashboard"))

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))



@bp.route("/login/local", methods=["POST"])
def login_local():
    username = request.form["username"]
    password = request.form["password"]

    result = authenticate_local(username, password)

    if result == "PENDING":
        flash("Usuário aguardando aprovação", "warning")
        return redirect(url_for("auth.login"))

    if not result:
        flash("Usuário ou senha inválidos", "danger")
        return redirect(url_for("auth.login"))

    login_user(User(result))
    return redirect(url_for("pages.dashboard"))


@bp.route("/register", methods=["POST"])
def register():
    try:
        user = register_user(request.form)
        flash(
            f"Usuário {user['username']} criado. Aguardando aprovação",
            "success"
        )
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("auth.login"))


@bp.route("/admin/users")
@login_required
@admin_required
def admin_users():
    search = request.args.get("q")
    users = list_pending_users(search)
    return render_template("auth/users_admin.html", users=users)

@bp.route("/admin/users/<int:user_id>/approve")
@login_required
def approve_user_route(user_id):
    if not current_user.is_admin:
        return redirect(url_for("pages.dashboard"))

    approve_user(user_id)
    flash("Usuário aprovado com sucesso", "success")
    return redirect(url_for("auth.admin_users"))


@bp.route("/admin/users/<int:user_id>/deny")
@login_required
def reject_user_route(user_id):
    if not current_user.is_admin:
        return redirect(url_for("pages.dashboard"))

    deny_user(user_id)
    flash("Usuário removido", "info")
    return redirect(url_for("auth.admin_users"))


@bp.route("/admin/users/all")
@login_required
@admin_required
def admin_users_all():
    """
    Página para exibir TODOS os usuários (ativos e pendentes)
    """
    search = request.args.get("q")
    users = list_all_users(search)
    return render_template("auth/users_all.html", users=users)


# experiência login mobile 
@bp.route("/login/mobile")
def login_mobile_choice():
    return render_template("auth/mobile/login_choice.html")


@bp.route("/login/mobile/form")
def login_mobile_form():
    return render_template("auth/mobile/login_form.html")


@bp.route("/register/mobile")
def register_mobile_form():
    return render_template("auth/mobile/register_form.html")
