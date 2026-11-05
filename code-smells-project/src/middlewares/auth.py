"""Proteção de rotas administrativas por token (header X-Admin-Token)."""
import hmac
from functools import wraps

from flask import current_app, request

from src.errors import ForbiddenError


def require_admin_token(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        esperado = current_app.config.get("ADMIN_TOKEN") or ""
        recebido = request.headers.get("X-Admin-Token", "")
        if not esperado or not hmac.compare_digest(recebido.encode(), esperado.encode()):
            raise ForbiddenError("Acesso restrito")
        return view(*args, **kwargs)

    return wrapper
