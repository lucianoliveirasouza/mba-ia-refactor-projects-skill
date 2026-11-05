import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils.errors import AppError

logger = logging.getLogger(__name__)

HTTP_ERROR_MESSAGES = {
    404: 'Recurso não encontrado',
    405: 'Método não permitido',
}


def register_error_handlers(app, session):
    """Converte exceções em respostas `{'error': msg}` e desfaz a transação pendente."""

    @app.errorhandler(AppError)
    def handle_app_error(err):
        session.rollback()
        return jsonify({'error': err.message}), err.status

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        session.rollback()
        return jsonify({'error': HTTP_ERROR_MESSAGES.get(err.code, err.name)}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        session.rollback()
        logger.exception('Erro não tratado')
        return jsonify({'error': 'Erro interno'}), 500
