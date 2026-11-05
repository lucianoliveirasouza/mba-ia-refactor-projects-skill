const express = require('express');
const config = require('./config');
const { createLogger } = require('./utils/logger');
const { openDatabase } = require('./database/connection');

const { createUserModel } = require('./models/userModel');
const { createCourseModel } = require('./models/courseModel');
const { createEnrollmentModel } = require('./models/enrollmentModel');
const { createPaymentModel } = require('./models/paymentModel');
const { createAuditLogModel } = require('./models/auditLogModel');

const { createPaymentService } = require('./services/paymentService');

const { createCheckoutController } = require('./controllers/checkoutController');
const { createReportController } = require('./controllers/reportController');
const { createUserController } = require('./controllers/userController');

const { createCheckoutRoutes } = require('./routes/checkoutRoutes');
const { createAdminRoutes } = require('./routes/adminRoutes');
const { createUserRoutes } = require('./routes/userRoutes');

const { createRequireAdmin } = require('./middlewares/auth');
const { createErrorHandler } = require('./middlewares/errorHandler');

/** Composition root: único lugar que conhece as implementações concretas. */
async function createApp(appConfig = config) {
    const logger = createLogger(appConfig.logLevel);
    const db = await openDatabase(appConfig.dbPath);

    const userModel = createUserModel(db);
    const courseModel = createCourseModel(db);
    const enrollmentModel = createEnrollmentModel(db);
    const paymentModel = createPaymentModel(db);
    const auditLogModel = createAuditLogModel(db);

    const paymentService = createPaymentService({ gatewayKey: appConfig.paymentGatewayKey, logger });

    const checkoutController = createCheckoutController({
        db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentService, logger,
    });
    const reportController = createReportController({ enrollmentModel });
    const userController = createUserController({ db, userModel, auditLogModel });

    const requireAdmin = createRequireAdmin(appConfig.adminToken);
    if (!appConfig.adminToken) {
        logger.warn('ADMIN_TOKEN não configurado: rotas administrativas estão bloqueadas');
    }

    const app = express();
    app.use(express.json());
    app.use('/api', createCheckoutRoutes(checkoutController));
    app.use('/api', createAdminRoutes(reportController, requireAdmin));
    app.use('/api', createUserRoutes(userController, requireAdmin));
    app.use(createErrorHandler(logger));

    return { app, db, logger };
}

if (require.main === module) {
    createApp()
        .then(({ app, logger }) => {
            app.listen(config.port, () => logger.info(`LMS API rodando na porta ${config.port}`));
        })
        .catch((err) => {
            console.error('Falha ao iniciar a aplicação', err);
            process.exit(1);
        });
}

module.exports = { createApp };
