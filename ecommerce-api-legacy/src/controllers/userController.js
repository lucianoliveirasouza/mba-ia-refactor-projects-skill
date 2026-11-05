const { NotFoundError } = require('../errors/AppError');

function createUserController({ userModel, auditLogModel, db }) {
    return {
        async deleteUser(id) {
            await db.transaction(async (tx) => {
                const deleted = await userModel.deleteById(id, tx);
                if (!deleted) throw new NotFoundError('Usuário não encontrado');
                await auditLogModel.record(`Usuário ${id} removido`, tx);
            });
            return 'Usuário deletado';
        },
    };
}

module.exports = { createUserController };
