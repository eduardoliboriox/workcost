from flask import Flask
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import Config
from app.extensions import login_manager

from app.routes.pages import bp as pages_bp
from app.routes.api import bp as api_bp
from app.auth.routes import bp as auth_bp
from app.auth.models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_port=1,
        x_prefix=1
    )

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY não configurada")

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow}

    # 📌 Blueprints
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # CLI commands
    from app.cli.employees_importer import import_employees
    app.cli.add_command(import_employees)

    from app.cli.employees_code_generator import generate_employee_codes
    app.cli.add_command(generate_employee_codes)

    return app
