"""Configuração da aplicação lida de variáveis de ambiente (com `.env` opcional).

Os defaults servem apenas para desenvolvimento local; em produção defina
todas as variáveis listadas em `.env.example`.
"""
import os

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def _as_list(value):
    return [item.strip() for item in value.split(',') if item.strip()]


class Settings:
    def __init__(self, env=None):
        env = os.environ if env is None else env

        self.SECRET_KEY = env.get('SECRET_KEY', 'dev-only-change-me')
        self.DATABASE_URL = env.get('DATABASE_URL', 'sqlite:///tasks.db')

        self.DEBUG = _as_bool(env.get('FLASK_DEBUG'), default=False)
        self.HOST = env.get('HOST', '0.0.0.0')
        self.PORT = int(env.get('PORT', '5000'))
        self.LOG_LEVEL = env.get('LOG_LEVEL', 'INFO').upper()

        self.CORS_ORIGINS = _as_list(env.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000'))

        self.TOKEN_MAX_AGE_SECONDS = int(env.get('TOKEN_MAX_AGE_SECONDS', str(60 * 60 * 24)))

        # SMTP: envio de email fica desabilitado enquanto SMTP_HOST não for definido.
        self.SMTP_HOST = env.get('SMTP_HOST', '')
        self.SMTP_PORT = int(env.get('SMTP_PORT', '587'))
        self.SMTP_USER = env.get('SMTP_USER', '')
        self.SMTP_PASSWORD = env.get('SMTP_PASSWORD', '')
