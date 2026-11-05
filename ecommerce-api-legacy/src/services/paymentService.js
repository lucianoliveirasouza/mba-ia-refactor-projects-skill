const { PAYMENT_STATUS, APPROVED_CARD_PREFIX } = require('../constants');

const maskCard = (cardNumber) => `**** ${cardNumber.slice(-4)}`;

/** Gateway de pagamento simulado. A chave é injetada e nunca é logada. */
function createPaymentService({ gatewayKey, logger }) {
    return {
        authorize({ cardNumber, amount }) {
            logger.info(`Processando pagamento de ${amount} com cartão ${maskCard(cardNumber)}`);
            if (!gatewayKey) logger.debug('PAYMENT_GATEWAY_KEY não configurada (modo simulado)');
            return cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
        },
    };
}

module.exports = { createPaymentService };
