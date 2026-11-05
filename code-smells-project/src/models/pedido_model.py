"""Acesso a dados de pedidos e itens (escritas múltiplas sempre em transação)."""
from src.constants import StatusPedido
from src.errors import EstoqueInsuficienteError

_SELECT_PEDIDOS_COM_ITENS = """
    SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
           i.id AS item_id, i.produto_id, i.quantidade, i.preco_unitario,
           COALESCE(pr.nome, 'Desconhecido') AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
"""


def _agrupar_pedidos(rows):
    pedidos = {}
    for row in rows:
        pedido = pedidos.setdefault(row["id"], {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": [],
        })
        if row["item_id"] is not None:
            pedido["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"],
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())


class PedidoModel:
    def __init__(self, get_connection):
        self._conn = get_connection

    def listar(self, usuario_id=None):
        sql, params = _SELECT_PEDIDOS_COM_ITENS, ()
        if usuario_id is not None:
            sql += " WHERE p.usuario_id = ?"
            params = (usuario_id,)
        sql += " ORDER BY p.id, i.id"
        return _agrupar_pedidos(self._conn().execute(sql, params).fetchall())

    def buscar_status(self, pedido_id):
        row = self._conn().execute("SELECT status FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
        return row["status"] if row else None

    def criar(self, usuario_id, total, itens):
        """Cria pedido + itens e baixa o estoque atomicamente.

        `itens`: lista de dicts com produto_id, quantidade e preco_unitario.
        Lança EstoqueInsuficienteError (com rollback) se algum produto não tiver saldo.
        """
        conn = self._conn()
        with conn:
            cursor = conn.execute(
                "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
                (usuario_id, StatusPedido.PENDENTE, total),
            )
            pedido_id = cursor.lastrowid
            for item in itens:
                conn.execute(
                    "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                    (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
                )
                baixa = conn.execute(
                    "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                    (item["quantidade"], item["produto_id"], item["quantidade"]),
                )
                if baixa.rowcount == 0:
                    raise EstoqueInsuficienteError(item["produto_id"])
        return pedido_id

    def atualizar_status(self, pedido_id, novo_status, devolver_estoque=False):
        conn = self._conn()
        with conn:
            conn.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
            if devolver_estoque:
                conn.execute(
                    """
                    UPDATE produtos
                    SET estoque = estoque + (
                        SELECT SUM(i.quantidade) FROM itens_pedido i
                        WHERE i.pedido_id = ? AND i.produto_id = produtos.id
                    )
                    WHERE id IN (SELECT produto_id FROM itens_pedido WHERE pedido_id = ?)
                    """,
                    (pedido_id, pedido_id),
                )

    def totais_vendas(self):
        row = self._conn().execute(
            """
            SELECT COUNT(*) AS total_pedidos,
                   COALESCE(SUM(total), 0) AS faturamento,
                   COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS pendentes,
                   COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS aprovados,
                   COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS cancelados
            FROM pedidos
            """,
            (StatusPedido.PENDENTE, StatusPedido.APROVADO, StatusPedido.CANCELADO),
        ).fetchone()
        return dict(row)
