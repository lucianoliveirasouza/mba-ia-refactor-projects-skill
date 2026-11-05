"""Relatório de vendas: regras de desconto e indicadores."""
from src.constants import FAIXAS_DESCONTO


def calcular_desconto(faturamento):
    for limite, taxa in FAIXAS_DESCONTO:
        if faturamento > limite:
            return faturamento * taxa
    return 0


class RelatorioController:
    def __init__(self, pedido_model):
        self.pedidos = pedido_model

    def vendas(self):
        totais = self.pedidos.totais_vendas()
        faturamento = totais["faturamento"]
        total_pedidos = totais["total_pedidos"]
        desconto = calcular_desconto(faturamento)
        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": totais["pendentes"],
            "pedidos_aprovados": totais["aprovados"],
            "pedidos_cancelados": totais["cancelados"],
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos else 0,
        }
