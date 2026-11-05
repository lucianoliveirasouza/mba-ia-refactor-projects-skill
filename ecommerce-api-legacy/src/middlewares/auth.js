const crypto = require('crypto');
const { ADMIN_TOKEN_HEADER } = require('../constants');
const { UnauthorizedError, ForbiddenError } = require('../errors/AppError');

function safeEqual(a, b) {
    const left = Buffer.from(a);
    const right = Buffer.from(b);
    return left.length === right.length && crypto.timingSafeEqual(left, right);
}

/** Protege rotas administrativas/destrutivas. Sem ADMIN_TOKEN configurado, todas ficam bloqueadas. */
function createRequireAdmin(adminToken) {
    return (req, res, next) => {
        const provided = req.get(ADMIN_TOKEN_HEADER);
        if (!provided) return next(new UnauthorizedError());
        if (!adminToken || !safeEqual(provided, adminToken)) return next(new ForbiddenError());
        return next();
    };
}

module.exports = { createRequireAdmin };
