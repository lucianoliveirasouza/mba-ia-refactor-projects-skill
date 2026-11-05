"""Rotas HTTP de produtos."""
from flask import Blueprint, jsonify, request

from src.views.validators import validar_filtros_busca, validar_produto


def create_produto_blueprint(controller):
    bp = Blueprint("produtos", __name__)

    @bp.get("/produtos")
    def listar_produtos():
        return jsonify({"dados": controller.listar(), "sucesso": True}), 200

    # Declarada antes de /produtos/<id> (ordem original preservada).
    @bp.get("/produtos/busca")
    def buscar_produtos():
        resultados = controller.pesquisar(**validar_filtros_busca(request.args))
        return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200

    @bp.get("/produtos/<int:produto_id>")
    def buscar_produto(produto_id):
        return jsonify({"dados": controller.buscar(produto_id), "sucesso": True}), 200

    @bp.post("/produtos")
    def criar_produto():
        produto_id = controller.criar(validar_produto(request.get_json(silent=True)))
        return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201

    @bp.put("/produtos/<int:produto_id>")
    def atualizar_produto(produto_id):
        controller.buscar(produto_id)  # contrato: 404 tem precedência sobre erro de validação
        controller.atualizar(produto_id, validar_produto(request.get_json(silent=True)))
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    @bp.delete("/produtos/<int:produto_id>")
    def deletar_produto(produto_id):
        controller.deletar(produto_id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200

    return bp
