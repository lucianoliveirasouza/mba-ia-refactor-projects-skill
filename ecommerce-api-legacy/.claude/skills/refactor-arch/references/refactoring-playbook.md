# Playbook de Refatoração (Fase 3)

Transformações concretas para cada anti-pattern do catálogo. Exemplos em Python/Flask e Node/Express — **adapte** à stack, ao idioma dos nomes e às convenções do projeto. Aplique sempre preservando o contrato (ver `mvc-guidelines.md`).

| ID | Padrão | Resolve |
|---|---|---|
| PB-01 | Extrair configuração para env/config | AP-01, AP-12 |
| PB-02 | Queries parametrizadas | AP-02 |
| PB-03 | Decompor God Class em camadas por domínio | AP-03 |
| PB-04 | Mover regra de negócio para controller/service | AP-07 |
| PB-05 | Error handler centralizado + exceções de domínio | AP-15 |
| PB-06 | Injeção de dependência / composition root / conexão por request | AP-08, AP-09 |
| PB-07 | Eliminar N+1 com JOIN / eager loading / agregação | AP-13 |
| PB-08 | Hash seguro de senha | AP-06 |
| PB-09 | Serialização por whitelist e proteção de endpoints perigosos | AP-04, AP-05 |
| PB-10 | Callback hell → async/await | AP-10 |
| PB-11 | Transações e integridade referencial | AP-11 |
| PB-12 | Camada de validação única | AP-14 |
| PB-13 | Substituir APIs deprecated | AP-17 |
| PB-14 | Constantes/enums, nomes claros e condicionais simples | AP-18, AP-19, AP-22 |
| PB-15 | Logging estruturado no lugar de print | AP-20, AP-05 |
| PB-16 | Remover duplicação e código morto | AP-16, AP-21 |

---

## PB-01 — Extrair configuração para env/config

**Antes (Python)**
```python
app = Flask(__name__)
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
...
app.run(host="0.0.0.0", port=5000, debug=True)
```
**Depois**
```python
# src/config/settings.py
import os

class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

# app.py
settings = Settings()
app = create_app(settings)
app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
```
**Antes (Node)**
```js
const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_123", port: 3000 };
```
**Depois**
```js
// src/config/index.js
module.exports = Object.freeze({
  port: Number(process.env.PORT) || 3000,
  dbPath: process.env.DB_PATH || ':memory:',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  smtpUser: process.env.SMTP_USER || '',
});
```
Crie `.env.example` com todas as chaves (sem valores reais). Se `python-dotenv`/`dotenv` já for dependência, carregue o `.env` no composition root; não adicione dependências novas sem necessidade.

## PB-02 — Queries parametrizadas

**Antes**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
query += " AND (nome LIKE '%" + termo + "%')"
```
**Depois**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))

conditions, params = ["1=1"], []
if termo:
    conditions.append("(nome LIKE ? OR descricao LIKE ?)")
    params += [f"%{termo}%", f"%{termo}%"]
if categoria:
    conditions.append("categoria = ?")
    params.append(categoria)
cursor.execute(f"SELECT * FROM produtos WHERE {' AND '.join(conditions)}", params)
```
**Node**
```js
// Antes: db.get(`SELECT * FROM users WHERE email = '${email}'`)
db.get('SELECT * FROM users WHERE email = ?', [email]);
```
Apenas fragmentos **fixos** do código podem ser interpolados (como as condições acima); valores vão sempre em parâmetros.

## PB-03 — Decompor God Class / God Module em camadas por domínio

**Antes** — um arquivo/classe com schema, rotas e regra:
```js
class AppManager {
  constructor() { this.db = new sqlite3.Database(':memory:'); }
  initDb() { /* CREATE TABLE + seeds */ }
  setupRoutes(app) {
    app.post('/api/checkout', (req, res) => { /* validação + SQL + pagamento + auditoria */ });
    app.get('/api/admin/financial-report', (req, res) => { /* SQL em loop + agregação */ });
  }
}
```
**Depois**
```
src/database/connection.js     ← initDb (schema + seed)
src/models/courseModel.js      ← findActiveById
src/models/userModel.js        ← findByEmail, create, deleteById
src/models/enrollmentModel.js  ← create, financialReportRows
src/services/paymentService.js ← processPayment(card, amount)
src/controllers/checkoutController.js ← caso de uso checkout
src/controllers/reportController.js   ← relatório financeiro
src/routes/*.js                ← só HTTP
src/app.js                     ← composition root
```
Procedimento: (1) liste as funções/métodos do arquivo e marque o papel de cada um; (2) agrupe por domínio; (3) mova SQL → models, regra → controllers/services, rotas → routes; (4) ligue tudo no composition root; (5) só então remova o arquivo antigo.

Python (funções de `models.py` com 4 domínios):
```
models.py: get_todos_produtos, criar_pedido, relatorio_vendas, login_usuario ...
→ src/models/produto_model.py, usuario_model.py, pedido_model.py
→ src/controllers/produto_controller.py, usuario_controller.py, pedido_controller.py, relatorio_controller.py
```

## PB-04 — Mover regra de negócio para controller/service

**Antes** (cálculo de desconto dentro do model e notificações dentro do handler)
```python
def relatorio_vendas():            # models.py
    ...
    if faturamento > 10000: desconto = faturamento * 0.1
    elif faturamento > 5000: desconto = faturamento * 0.05

def criar_pedido():                # controllers.py (handler HTTP)
    dados = request.get_json()
    resultado = models.criar_pedido(dados["usuario_id"], dados["itens"])
    print("ENVIANDO EMAIL: Pedido ...")
    return jsonify(...), 201
```
**Depois**
```python
# models/pedido_model.py — só dados
def totais_vendas(conn): ...   # COUNT/SUM/GROUP BY status

# controllers/relatorio_controller.py — regra
DISCOUNT_TIERS = ((10000, 0.10), (5000, 0.05), (1000, 0.02))

def calcular_desconto(faturamento):
    for limite, taxa in DISCOUNT_TIERS:
        if faturamento > limite:
            return faturamento * taxa
    return 0

# controllers/pedido_controller.py
class PedidoController:
    def __init__(self, pedido_model, notifier):
        self.pedido_model, self.notifier = pedido_model, notifier
    def criar(self, usuario_id, itens):
        pedido = self.pedido_model.criar(usuario_id, itens)
        self.notifier.pedido_criado(pedido)
        return pedido

# views/pedido_routes.py — só HTTP
@bp.post("/pedidos")
def criar_pedido():
    dados = validar_pedido(request.get_json(silent=True))
    pedido = current_app.extensions["controllers"].pedido.criar(**dados)
    return jsonify({"dados": pedido, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201
```
(Qualquer forma de obter o controller injetado serve: closure em factory de blueprint, `app.extensions`, container simples.)

## PB-05 — Error handler centralizado + exceções de domínio

**Antes**
```python
def buscar_produto(id):
    try:
        produto = models.get_produto_por_id(id)
        if produto: return jsonify({"dados": produto}), 200
        return jsonify({"erro": "Produto não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
```
**Depois**
```python
# src/middlewares/error_handler.py
class AppError(Exception):
    status = 400
    def __init__(self, message): super().__init__(message); self.message = message
class ValidationError(AppError): status = 400
class NotFoundError(AppError): status = 404
class ConflictError(AppError): status = 409

def register_error_handlers(app, error_key="erro"):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({error_key: err.message, "sucesso": False}), err.status

    @app.errorhandler(404)
    def handle_404(_): return jsonify({error_key: "Recurso não encontrado"}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception("Unhandled error")
        return jsonify({error_key: "Erro interno do servidor"}), 500

# rota
@bp.get("/produtos/<int:id>")
def buscar_produto(id):
    return jsonify({"dados": controller.buscar(id), "sucesso": True}), 200   # controller lança NotFoundError
```
**Node (Express 4)**
```js
// middlewares/asyncHandler.js
module.exports = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

// middlewares/errorHandler.js
class AppError extends Error { constructor(message, status = 400) { super(message); this.status = status; } }
function errorHandler(err, req, res, next) {
  if (err instanceof AppError) return res.status(err.status).send(err.message);
  console.error(err);
  return res.status(500).send('Erro interno');
}
module.exports = { AppError, errorHandler };
// app.js: app.use(errorHandler) DEPOIS das rotas
```
Mantenha o formato de erro que o contrato já usa (JSON com `erro`/`error`, ou texto puro) e os mesmos status.

## PB-06 — Injeção de dependência, composition root e conexão sem global mutável

**Antes**
```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect("loja.db", check_same_thread=False)
    return db_connection
```
**Depois (conexão por request + factory)**
```python
# src/database/connection.py
import sqlite3
from flask import g, current_app

def get_connection():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_connection(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()

def init_app(app):
    app.teardown_appcontext(close_connection)
    with app.app_context():
        create_schema_and_seed(get_connection())

# src/app.py
def create_app(settings=None):
    settings = settings or Settings()
    app = Flask(__name__)
    app.config.from_object(settings)
    CORS(app, origins=settings.CORS_ORIGINS)
    database.init_app(app)
    register_error_handlers(app)
    register_routes(app)
    return app
```
**Node**
```js
// Antes: class AppManager { constructor() { this.db = new sqlite3.Database(':memory:'); } }
// Depois: dependências criadas uma vez no composition root e injetadas
async function createApp() {
  const db = await openDatabase(config.dbPath);
  const userModel = createUserModel(db);
  const checkoutController = createCheckoutController({ userModel, courseModel, enrollmentModel, paymentService });
  const app = express();
  app.use(express.json());
  app.use('/api', createCheckoutRoutes(checkoutController));
  app.use(errorHandler);
  return app;
}
```
Caches/contadores globais (`globalCache`, `totalRevenue`) viram dependências explícitas injetadas — ou são removidos se não forem lidos por ninguém.

## PB-07 — Eliminar N+1

**Antes (SQL cru)**
```python
for pedido in pedidos:
    itens = conn.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido["id"],))
    for item in itens:
        prod = conn.execute("SELECT nome FROM produtos WHERE id = ?", (item["produto_id"],))
```
**Depois**
```python
rows = conn.execute("""
    SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
           i.produto_id, i.quantidade, i.preco_unitario,
           COALESCE(pr.nome, 'Desconhecido') AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
    ORDER BY p.id
""").fetchall()
# agrupar em Python por p.id preservando o formato de resposta original
```
**Depois (SQLAlchemy)**
```python
from sqlalchemy.orm import joinedload
tasks = db.session.execute(
    db.select(Task).options(joinedload(Task.user), joinedload(Task.category))
).scalars().all()

# contagens por status: 1 query em vez de N
rows = db.session.execute(db.select(Task.status, db.func.count()).group_by(Task.status)).all()
counts = {status: n for status, n in rows}
```
**Node:** substitua `forEach` com `db.get` aninhado por um único `SELECT ... JOIN ... ` e agregue em memória.

## PB-08 — Hash seguro de senha

**Antes**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
# ou INSERT INTO usuarios (..., senha) VALUES (..., '123456')
```
**Depois (Python — werkzeug já vem com Flask)**
```python
from werkzeug.security import generate_password_hash, check_password_hash
def set_password(self, pwd): self.password = generate_password_hash(pwd)
def check_password(self, pwd): return check_password_hash(self.password, pwd)

# login com SQL cru: busque por e-mail e verifique o hash em código
row = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
if row and check_password_hash(row["senha"], senha): ...
```
**Node (sem dependência nova)**
```js
const crypto = require('crypto');
function hashPassword(pwd) {
  const salt = crypto.randomBytes(16).toString('hex');
  return `${salt}:${crypto.scryptSync(pwd, salt, 64).toString('hex')}`;
}
function verifyPassword(pwd, stored) {
  const [salt, hash] = stored.split(':');
  return crypto.timingSafeEqual(Buffer.from(hash, 'hex'), crypto.scryptSync(pwd, salt, 64));
}
```
**Obrigatório:** atualize seeds para gravar hashes; garanta que o login com as credenciais de seed continua funcionando; se houver banco persistente antigo com senhas em texto/MD5, documente que é preciso recriá-lo (rodar seed / apagar o `.db`).

## PB-09 — Serialização por whitelist e proteção de endpoints perigosos

**Antes**
```python
def to_dict(self):
    return {"id": self.id, "email": self.email, "password": self.password, ...}

@app.route("/health")
def health(): return jsonify({"status": "ok", "secret_key": "minha-chave..."})

@app.route("/admin/query", methods=["POST"])
def executar_query(): cursor.execute(request.get_json()["sql"])
```
**Depois**
```python
PUBLIC_USER_FIELDS = ("id", "nome", "email", "tipo", "criado_em")
def serialize_user(user): return {k: user[k] for k in PUBLIC_USER_FIELDS}

@bp.get("/health")
def health(): return jsonify({"status": "ok", "database": controller.db_status()})

# middlewares/auth.py
def require_admin_token(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        expected = current_app.config.get("ADMIN_TOKEN")
        if not expected or request.headers.get("X-Admin-Token") != expected:
            raise ForbiddenError("Acesso restrito")
        return view(*args, **kwargs)
    return wrapper

@bp.post("/admin/reset-db")
@require_admin_token
def reset_database(): ...
```
Endpoints de execução arbitrária (SQL livre, `eval`): mantenha a rota respondendo (contrato) mas **desabilitada por padrão** (403/404 a menos que um flag de ambiente explícito e token admin estejam configurados). Registre em "Contract Changes". Nunca logue cartão/senha/chave; mascare (`**** 4444`).

## PB-10 — Callback hell → async/await

**Antes**
```js
db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
  db.get("SELECT id FROM users WHERE email = ?", [e], (err, user) => {
    db.run("INSERT INTO enrollments ...", [userId, cid], function (err) {
      self.db.run("INSERT INTO payments ...", [this.lastID, ...], function (err) { res.json(...) });
    });
  });
});
```
**Depois**
```js
// database/connection.js — wrapper Promise
function wrap(db) {
  return {
    get: (sql, p = []) => new Promise((ok, ko) => db.get(sql, p, (e, row) => (e ? ko(e) : ok(row)))),
    all: (sql, p = []) => new Promise((ok, ko) => db.all(sql, p, (e, rows) => (e ? ko(e) : ok(rows)))),
    run: (sql, p = []) => new Promise((ok, ko) => db.run(sql, p, function (e) { e ? ko(e) : ok({ lastID: this.lastID, changes: this.changes }); })),
  };
}

// controllers/checkoutController.js
async checkout({ name, email, password, courseId, card }) {
  const course = await courseModel.findActiveById(courseId);
  if (!course) throw new AppError('Curso não encontrado', 404);
  const user = (await userModel.findByEmail(email)) ?? (await userModel.create({ name, email, password }));
  if (!paymentService.authorize(card)) throw new AppError('Pagamento recusado', 400);
  const enrollmentId = await enrollmentModel.enrollWithPayment(user.id, course.id, course.price);
  return { msg: 'Sucesso', enrollment_id: enrollmentId };
}

// routes/checkoutRoutes.js
router.post('/checkout', asyncHandler(async (req, res) => {
  const { usr, eml, pwd, c_id, card } = req.body;          // contrato externo preservado
  if (!usr || !eml || !c_id || !card) throw new AppError('Bad Request', 400);
  res.status(200).json(await controller.checkout({ name: usr, email: eml, password: pwd, courseId: c_id, card }));
}));
```

## PB-11 — Transações e integridade referencial

**Antes**
```python
for item in itens:                     # valida e pode retornar erro no meio
    ...
cursor.execute("INSERT INTO pedidos ...")
for item in itens:
    cursor.execute("INSERT INTO itens_pedido ...")
    cursor.execute("UPDATE produtos SET estoque = estoque - ...")
db.commit()
```
**Depois**
```python
def criar(self, usuario_id, itens):
    conn = self.conn
    try:
        conn.execute("BEGIN")
        ...  # validações e inserts parametrizados
        conn.commit()
    except Exception:
        conn.rollback()
        raise
```
SQLAlchemy: um único `db.session.commit()` no fim do caso de uso; `rollback()` no error handler. Node: `await db.run('BEGIN')` … `COMMIT`/`ROLLBACK` no `catch`.
Deletes de entidade pai: apague dependentes na mesma transação (ou configure `ON DELETE CASCADE`/`cascade="all, delete-orphan"`).

## PB-12 — Camada de validação única

**Antes** (regras repetidas e divergentes em create/update, comparação de tipos frágil)
```python
if len(title) < 3: return jsonify({'error': 'Título muito curto'}), 400
if priority < 1 or priority > 5: ...            # TypeError se vier "3"
if status not in ['pending', 'in_progress', 'done', 'cancelled']: ...
```
**Depois**
```python
# validators/task_validator.py (ou schemas com marshmallow/pydantic se já forem dependência)
from src.constants import TaskStatus, PRIORITY_MIN, PRIORITY_MAX, TITLE_MIN, TITLE_MAX

def validate_task_payload(data, partial=False):
    if not isinstance(data, dict):
        raise ValidationError("Dados inválidos")
    cleaned = {}
    if "title" in data or not partial:
        title = (data.get("title") or "").strip()
        if not title: raise ValidationError("Título é obrigatório")
        if not TITLE_MIN <= len(title) <= TITLE_MAX:
            raise ValidationError(f"Título deve ter entre {TITLE_MIN} e {TITLE_MAX} caracteres")
        cleaned["title"] = title
    if "priority" in data:
        try: priority = int(data["priority"])
        except (TypeError, ValueError): raise ValidationError("Prioridade inválida")
        if not PRIORITY_MIN <= priority <= PRIORITY_MAX:
            raise ValidationError("Prioridade deve ser entre 1 e 5")
        cleaned["priority"] = priority
    ...
    return cleaned
```
Reaproveite helpers de validação já existentes no projeto em vez de duplicá-los. Mantenha as mensagens de erro existentes quando fizer sentido (contrato).

## PB-13 — Substituir APIs deprecated

```python
# Antes
from datetime import datetime
created_at = db.Column(db.DateTime, default=datetime.utcnow)
task = Task.query.get(task_id)

# Depois
from datetime import datetime, timezone
def utcnow():  # naive UTC: compatível com valores já gravados e com comparações existentes
    return datetime.now(timezone.utc).replace(tzinfo=None)
created_at = db.Column(db.DateTime, default=utcnow)
task = db.session.get(Task, task_id)
```
```js
// Antes
const b = new Buffer(pwd); app.del('/x', h); res.send(404, 'x'); const u = url.parse(req.url);
// Depois
const b = Buffer.from(pwd); app.delete('/x', h); res.status(404).send('x'); const u = new URL(req.url, 'http://localhost');
```
Ao trocar `Model.query.get` por `db.session.get`, troque também o padrão `get_or_404` por lookup + `NotFoundError`.

## PB-14 — Constantes, nomes claros e condicionais simples

```python
# Antes
if novo_status not in ["pendente", "aprovado", "enviado", "entregue", "cancelado"]: ...
def is_admin(self):
    if self.role == 'admin': return True
    else: return False
let u = req.body.usr; let cc = req.body.card;

# Depois
class PedidoStatus:
    PENDENTE, APROVADO, ENVIADO, ENTREGUE, CANCELADO = "pendente", "aprovado", "enviado", "entregue", "cancelado"
    ALL = (PENDENTE, APROVADO, ENVIADO, ENTREGUE, CANCELADO)

def is_admin(self): return self.role == Role.ADMIN
const { usr: name, eml: email, card: cardNumber } = req.body;   // nome interno claro, campo externo preservado

def is_overdue(self):
    return bool(self.due_date) and self.due_date < utcnow() and self.status not in TaskStatus.CLOSED
```
Um único módulo de constantes por projeto (ou por domínio); nada de listas de valores válidos repetidas.

## PB-15 — Logging no lugar de print

```python
# Antes
print("ERRO: " + str(e)); print("ENVIANDO EMAIL: Pedido " + str(pid))
# Depois
import logging
logger = logging.getLogger(__name__)
logger.exception("Falha ao criar pedido")
logger.info("Notificação de pedido criado enviada", extra={"pedido_id": pid})
```
```js
// Antes
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
// Depois
logger.info(`Processando pagamento com cartão final ${cardNumber.slice(-4)}`);  // nunca o número completo ou a chave
```
Configure o logging uma vez no composition root. Notificações simuladas por `print` viram um `NotificationService` (injetado) que loga — mantendo o comportamento observável.

## PB-16 — Remover duplicação e código morto

```python
# Antes: mesmo dict montado campo a campo em 4 funções + regra "overdue" copiada em 5 lugares
task_data = {'id': t.id, 'title': t.title, ...}
if t.due_date and t.due_date < datetime.utcnow() and t.status not in ('done', 'cancelled'): ...

# Depois
def serialize_task(task, *, with_relations=False):
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    if with_relations:
        data["user_name"] = task.user.name if task.user else None
        data["category_name"] = task.category.name if task.category else None
    return data
```
Remova imports sem uso, funções nunca chamadas e exports órfãos — confirme com Grep que não há referência antes de apagar. Preserve exatamente as chaves que cada endpoint retornava (alguns endpoints podem ter um subconjunto de campos; use parâmetros no serializer em vez de mudar o formato).
