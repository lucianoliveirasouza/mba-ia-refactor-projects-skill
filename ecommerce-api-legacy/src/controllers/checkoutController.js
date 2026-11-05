const { PAYMENT_STATUS } = require('../constants');
const { NotFoundError, ValidationError, AppError } = require('../errors/AppError');
const { hashPassword } = require('../utils/password');

function createCheckoutController({ db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentService, logger }) {
    return {
        async checkout({ name, email, password, courseId, cardNumber }) {
            const course = await courseModel.findActiveById(courseId);
            if (!course) throw new NotFoundError('Curso não encontrado');

            const existingUser = await userModel.findByEmail(email);
            if (!existingUser && !password) {
                throw new ValidationError('Senha obrigatória para novo usuário');
            }

            const status = paymentService.authorize({ cardNumber, amount: course.price });
            if (status !== PAYMENT_STATUS.PAID) throw new AppError('Pagamento recusado', 400);

            // Usuário + matrícula + pagamento + auditoria: tudo ou nada.
            const enrollmentId = await db.transaction(async (tx) => {
                // Relê dentro da transação (serializada) para evitar corrida entre checkouts do mesmo e-mail.
                let user = await userModel.findByEmail(email, tx);
                if (!user) {
                    if (!password) throw new ValidationError('Senha obrigatória para novo usuário');
                    user = await userModel.create({ name, email, passwordHash: hashPassword(password) }, tx);
                }
                const newEnrollmentId = await enrollmentModel.create({ userId: user.id, courseId: course.id }, tx);
                await paymentModel.create({ enrollmentId: newEnrollmentId, amount: course.price, status }, tx);
                await auditLogModel.record(`Checkout curso ${course.id} por ${user.id}`, tx);
                return newEnrollmentId;
            });

            logger.info(`Checkout concluído: matrícula ${enrollmentId} no curso "${course.title}"`);
            return { msg: 'Sucesso', enrollment_id: enrollmentId };
        },
    };
}

module.exports = { createCheckoutController };
