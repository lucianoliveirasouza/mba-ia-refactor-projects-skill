"""Casos de uso de produtos."""
import logging

from src.errors import NotFoundError

logger = logging.getLogger(__name__)


class ProdutoController:
    def __init__(self, produto_model):
        self.produtos = produto_model

    def listar(self):
        return self.produtos.listar()

    def buscar(self, produto_id):
        produto = self.produtos.buscar_por_id(produto_id)
        if not produto:
            raise NotFoundError("Produto não encontrado")
        return produto

    def pesquisar(self, termo, categoria, preco_min, preco_max):
        return self.produtos.buscar(termo, categoria, preco_min, preco_max)

    def criar(self, dados):
        produto_id = self.produtos.criar(**dados)
        logger.info("Produto criado com ID %s", produto_id)
        return produto_id

    def atualizar(self, produto_id, dados):
        self.buscar(produto_id)
        self.produtos.atualizar(produto_id, **dados)

    def deletar(self, produto_id):
        self.buscar(produto_id)
        self.produtos.deletar(produto_id)
        logger.info("Produto %s deletado", produto_id)
