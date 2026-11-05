"""Constantes de domínio da loja (fonte única para valores válidos e regras numéricas)."""

APP_VERSION = "1.0.0"

CATEGORIAS_VALIDAS = ("informatica", "moveis", "vestuario", "geral", "eletronicos", "livros")
CATEGORIA_PADRAO = "geral"
NOME_PRODUTO_MIN = 2
NOME_PRODUTO_MAX = 200


class StatusPedido:
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"
    TODOS = (PENDENTE, APROVADO, ENVIADO, ENTREGUE, CANCELADO)


class TipoUsuario:
    CLIENTE = "cliente"
    ADMIN = "admin"


# (faturamento mínimo exclusivo, taxa de desconto) — avaliadas da maior para a menor
FAIXAS_DESCONTO = (
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
)
