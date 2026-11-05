"""Configuração da aplicação lida de variáveis de ambiente (defaults seguros para dev)."""
import os
import secrets
from dataclasses import dataclass


def _env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def _env_list(name, default):
    raw = os.environ.get(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    SECRET_KEY: str
    DEBUG: bool
    APP_ENV: str
    HOST: str
    PORT: int
    DATABASE_PATH: str
    CORS_ORIGINS: tuple
    ADMIN_TOKEN: str
    ENABLE_ADMIN_QUERY: bool
    LOG_LEVEL: str

    @classmethod
    def from_env(cls):
        return cls(
            # Sem SECRET_KEY definida, gera uma chave aleatória por processo (nunca um literal no código).
            SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
            DEBUG=_env_bool("FLASK_DEBUG", False),
            APP_ENV=os.environ.get("APP_ENV", "development"),
            HOST=os.environ.get("HOST", "0.0.0.0"),
            PORT=int(os.environ.get("PORT", "5000")),
            DATABASE_PATH=os.environ.get("DATABASE_PATH", "loja.db"),
            CORS_ORIGINS=tuple(_env_list("CORS_ORIGINS", "*")),
            # Rotas /admin/* ficam bloqueadas (403) enquanto ADMIN_TOKEN não for definido.
            ADMIN_TOKEN=os.environ.get("ADMIN_TOKEN", ""),
            # /admin/query (SQL livre) exige, além do token, habilitação explícita.
            ENABLE_ADMIN_QUERY=_env_bool("ENABLE_ADMIN_QUERY", False),
            LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO").upper(),
        )
