"""Casos de uso de pedidos: criação (preço, estoque), listagem e mudança de status."""
from collections import Counter

from src.constants import StatusPedido
from src.errors import EstoqueInsuficienteError, NotFoundError, ValidationError


class PedidoController:
    def __init__(self, pedido_model, produto_model, usuario_model, notifier):
        self.pedidos = pedido_model
        self.produtos = produto_model
        self.usuarios = usuario_model
        self.notifier = notifier

    def criar(self, usuario_id, itens):
        if not self.usuarios.existe(usuario_id):
            raise ValidationError("Usuário " + str(usuario_id) + " não encontrado")

        produtos = self.produtos.buscar_por_ids(item["produto_id"] for item in itens)
        quantidade_por_produto = Counter()
        itens_precificados = []
        total = 0
        for item in itens:
            produto = produtos.get(item["produto_id"])
            if produto is None:
                raise ValidationError("Produto " + str(item["produto_id"]) + " não encontrado")
            quantidade_por_produto[produto["id"]] += item["quantidade"]
            if produto["estoque"] < quantidade_por_produto[produto["id"]]:
                raise ValidationError("Estoque insuficiente para " + produto["nome"])
            total += produto["preco"] * item["quantidade"]
            itens_precificados.append({**item, "preco_unitario": produto["preco"]})

        try:
            pedido_id = self.pedidos.criar(usuario_id, total, itens_precificados)
        except EstoqueInsuficienteError as erro:  # concorrência: saldo mudou entre a leitura e a baixa
            raise ValidationError("Estoque insuficiente para " + produtos[erro.produto_id]["nome"]) from erro

        self.notifier.pedido_criado(pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}

    def listar_todos(self):
        return self.pedidos.listar()

    def listar_por_usuario(self, usuario_id):
        return self.pedidos.listar(usuario_id=usuario_id)

    def atualizar_status(self, pedido_id, novo_status):
        status_atual = self.pedidos.buscar_status(pedido_id)
        if status_atual is None:
            raise NotFoundError("Pedido não encontrado")
        if status_atual == StatusPedido.CANCELADO and novo_status != StatusPedido.CANCELADO:
            raise ValidationError("Pedido cancelado não pode mudar de status")

        cancelando = novo_status == StatusPedido.CANCELADO and status_atual != StatusPedido.CANCELADO
        self.pedidos.atualizar_status(pedido_id, novo_status, devolver_estoque=cancelando)

        if novo_status == StatusPedido.APROVADO:
            self.notifier.pedido_aprovado(pedido_id)
        elif cancelando:
            self.notifier.pedido_cancelado(pedido_id)
