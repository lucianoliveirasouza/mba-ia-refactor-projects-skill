const fs = require('fs');
const path = require('path');

// Carrega um .env opcional na raiz do projeto (Node >= 20.12 / 21.7), sem dependência extra.
const envFile = path.resolve(__dirname, '..', '..', '.env');
if (fs.existsSync(envFile) && typeof process.loadEnvFile === 'function') {
    process.loadEnvFile(envFile);
}

module.exports = Object.freeze({
    port: Number(process.env.PORT) || 3000,
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    adminToken: process.env.ADMIN_TOKEN || '',
    logLevel: process.env.LOG_LEVEL || 'info',
});
