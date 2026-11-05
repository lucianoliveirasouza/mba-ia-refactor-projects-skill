const sqlite3 = require('sqlite3');
const { hashPassword } = require('../utils/password');
const { PAYMENT_STATUS } = require('../constants');

const SCHEMA = [
    'PRAGMA foreign_keys = ON',
    `CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        pass TEXT NOT NULL
    )`,
    `CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        price REAL NOT NULL,
        active INTEGER NOT NULL DEFAULT 1
    )`,
    `CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE
    )`,
    `CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY,
        enrollment_id INTEGER NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
        amount REAL NOT NULL,
        status TEXT NOT NULL
    )`,
    'CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)',
];

/** Adapta a API de callbacks do sqlite3 para Promises. */
function wrap(rawDb) {
    const db = {
        run: (sql, params = []) => new Promise((resolve, reject) => {
            rawDb.run(sql, params, function onRun(err) {
                if (err) return reject(err);
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        }),
        get: (sql, params = []) => new Promise((resolve, reject) => {
            rawDb.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
        }),
        all: (sql, params = []) => new Promise((resolve, reject) => {
            rawDb.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
        }),
        close: () => new Promise((resolve, reject) => rawDb.close((err) => (err ? reject(err) : resolve()))),
    };

    // Uma única conexão é compartilhada: transações são enfileiradas para nunca se sobreporem.
    let queue = Promise.resolve();
    db.transaction = (work) => {
        const result = queue.then(async () => {
            await db.run('BEGIN');
            try {
                const value = await work(db);
                await db.run('COMMIT');
                return value;
            } catch (err) {
                await db.run('ROLLBACK');
                throw err;
            }
        });
        queue = result.catch(() => {});
        return result;
    };

    return db;
}

async function seed(db) {
    const { count } = await db.get('SELECT COUNT(*) AS count FROM users');
    if (count > 0) return;

    await db.transaction(async (tx) => {
        await tx.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            ['Leonan', 'leonan@fullcycle.com.br', hashPassword('123')]);
        await tx.run('INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)',
            ['Clean Architecture', 997.0, 'Docker', 497.0]);
        await tx.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
        await tx.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (1, ?, ?)',
            [997.0, PAYMENT_STATUS.PAID]);
    });
}

async function openDatabase(dbPath) {
    const rawDb = await new Promise((resolve, reject) => {
        const instance = new sqlite3.Database(dbPath, (err) => (err ? reject(err) : resolve(instance)));
    });
    const db = wrap(rawDb);
    for (const statement of SCHEMA) {
        await db.run(statement);
    }
    await seed(db);
    return db;
}

module.exports = { openDatabase };
