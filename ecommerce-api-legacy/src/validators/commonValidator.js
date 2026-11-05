const { ValidationError } = require('../errors/AppError');

const isNonEmptyString = (value) => typeof value === 'string' && value.trim() !== '';

function parsePositiveInt(value) {
    const number = isNonEmptyString(value) ? Number(value) : value;
    return Number.isInteger(number) && number > 0 ? number : null;
}

function validateIdParam(value) {
    const id = parsePositiveInt(value);
    if (!id) throw new ValidationError('Bad Request');
    return id;
}

module.exports = { isNonEmptyString, parsePositiveInt, validateIdParam };
