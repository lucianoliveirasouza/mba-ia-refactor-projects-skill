const PAYMENT_STATUS = Object.freeze({
    PAID: 'PAID',
    DENIED: 'DENIED',
});

// Regra simulada do gateway: cartões iniciados em "4" são aprovados.
const APPROVED_CARD_PREFIX = '4';

const ADMIN_TOKEN_HEADER = 'X-Admin-Token';

const UNKNOWN_STUDENT_NAME = 'Unknown';

module.exports = { PAYMENT_STATUS, APPROVED_CARD_PREFIX, ADMIN_TOKEN_HEADER, UNKNOWN_STUDENT_NAME };
