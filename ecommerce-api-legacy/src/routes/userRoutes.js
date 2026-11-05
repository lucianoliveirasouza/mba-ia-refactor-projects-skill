const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');
const { validateIdParam } = require('../validators/commonValidator');

function createUserRoutes(userController, requireAdmin) {
    const router = express.Router();

    router.delete('/users/:id', requireAdmin, asyncHandler(async (req, res) => {
        const id = validateIdParam(req.params.id);
        res.send(await userController.deleteUser(id));
    }));

    return router;
}

module.exports = { createUserRoutes };
