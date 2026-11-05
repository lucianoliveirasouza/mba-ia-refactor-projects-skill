const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');
const { validateCheckoutPayload } = require('../validators/checkoutValidator');

function createCheckoutRoutes(checkoutController) {
    const router = express.Router();

    router.post('/checkout', asyncHandler(async (req, res) => {
        const input = validateCheckoutPayload(req.body);
        res.status(200).json(await checkoutController.checkout(input));
    }));

    return router;
}

module.exports = { createCheckoutRoutes };
