"""Rotas HTTP de sistema: index, health e administração (protegidas)."""
from flask import Blueprint, jsonify, request

from src.constants import APP_VERSION
from src.middlewares.auth import require_admin_token
from src.views.validators import validar_sql


def create_sistema_blueprint(controller):
    bp = Blueprint("sistema", __name__)

    @bp.get("/")
    def index():
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": APP_VERSION,
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        })

    @bp.get("/health")
    def health_check():
        status = controller.health()
        if status is None:
            return jsonify({"status": "erro", "database": "disconnected"}), 500
        return jsonify(status), 200

    @bp.post("/admin/reset-db")
    @require_admin_token
    def reset_database():
        controller.resetar_banco()
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200

    @bp.post("/admin/query")
    @require_admin_token
    def executar_query():
        linhas = controller.executar_query(validar_sql(request.get_json(silent=True)))
        if linhas is None:
            return jsonify({"mensagem": "Query executada", "sucesso": True}), 200
        return jsonify({"dados": linhas, "sucesso": True}), 200

    return bp
