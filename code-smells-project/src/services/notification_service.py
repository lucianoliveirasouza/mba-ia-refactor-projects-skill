"""Notificações de pedido (simuladas via log; ponto único para integrar e-mail/SMS/push)."""
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def pedido_criado(self, pedido_id, usuario_id):
        logger.info("Notificação (email/sms/push): pedido %s criado para usuário %s", pedido_id, usuario_id)

    def pedido_aprovado(self, pedido_id):
        logger.info("Notificação: pedido %s aprovado, preparar envio", pedido_id)

    def pedido_cancelado(self, pedido_id):
        logger.info("Notificação: pedido %s cancelado, estoque devolvido", pedido_id)
