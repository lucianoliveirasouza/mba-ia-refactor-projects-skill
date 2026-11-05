const { ValidationError } = require('../errors/AppError');
const { isNonEmptyString, parsePositiveInt } = require('./commonValidator');

/**
 * Valida o corpo do checkout. Os nomes externos do contrato (usr, eml, pwd, c_id, card)
 * são mapeados para nomes internos claros.
 */
function validateCheckoutPayload(body) {
    const { usr, eml, pwd, c_id: rawCourseId, card } = body || {};

    const cardNumber = typeof card === 'number' ? String(card) : card;
    const courseId = parsePositiveInt(rawCourseId);

    if (!isNonEmptyString(usr) || !isNonEmptyString(eml) || !courseId || !isNonEmptyString(cardNumber)) {
        throw new ValidationError('Bad Request');
    }
    if (pwd !== undefined && pwd !== null && typeof pwd !== 'string') {
        throw new ValidationError('Bad Request');
    }

    return {
        name: usr.trim(),
        email: eml.trim().toLowerCase(),
        password: pwd || null,
        courseId,
        cardNumber: cardNumber.replace(/\s+/g, ''),
    };
}

module.exports = { validateCheckoutPayload };
