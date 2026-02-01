from flask_login import UserMixin
from app.auth.repository import get_user_by_id

class User(UserMixin):
    def __init__(self, data: dict):
        self.id = data["id"]
        self.username = data["username"]
        self.email = data.get("email")
        self.full_name = data.get("full_name")

        self._is_active = data.get("is_active", False)
        self.is_admin = data.get("is_admin", False)
        self.extra_authorized = data.get("extra_authorized", False)

    @property
    def is_active(self):
        """
        Flask-Login chama isso automaticamente.
        NÃO pode ser atributo direto.
        """
        return self._is_active

    @staticmethod
    def get(user_id):
        data = get_user_by_id(user_id)
        return User(data) if data else None
