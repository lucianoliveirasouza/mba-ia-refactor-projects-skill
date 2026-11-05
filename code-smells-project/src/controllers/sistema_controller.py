"""Casos de uso de infraestrutura: health check e operações administrativas."""
import logging

from src.constants import APP_VERSION
from src.errors import DatabaseError, ForbiddenError, ValidationError

logger = logging.getLogger(__name__)


class SistemaController:
    def __init__(self, sistema_model, app_env, admin_query_habilitada):
        self.sistema = sistema_model
        self.app_env = app_env
        self.admin_query_habilitada = admin_query_habilitada

    def health(self):
        """Retorna o status da aplicação, ou None se o banco estiver indisponível."""
        try:
            contagens = self.sistema.contagens()
        except DatabaseError:
            logger.exception("Health check: falha ao acessar o banco")
            return None
        return {
            "status": "ok",
            "database": "connected",
            "counts": contagens,
            "versao": APP_VERSION,
            "ambiente": self.app_env,
        }

    def resetar_banco(self):
        self.sistema.resetar()
        logger.warning("Banco de dados resetado via endpoint administrativo")

    def executar_query(self, sql):
        if not self.admin_query_habilitada:
            raise ForbiddenError("Endpoint desabilitado")
        logger.warning("Execução de SQL administrativo")
        try:
            return self.sistema.executar_sql(sql)
        except DatabaseError as erro:
            raise ValidationError("Query inválida: " + str(erro)) from erro
