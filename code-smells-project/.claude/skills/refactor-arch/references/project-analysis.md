# Análise de Projeto — Heurísticas (Fase 1)

Objetivo: identificar com evidências **linguagem, framework, banco de dados, domínio, arquitetura atual, entry point e endpoints**. Todo campo do resumo deve vir de um arquivo lido, nunca de suposição.

## 1. Escopo de arquivos

Inclua: código da aplicação, manifestos, README, exemplos de requisição (`*.http`, coleções), scripts de seed/migração.

Exclua sempre: `node_modules/`, `venv/`, `.venv/`, `env/`, `__pycache__/`, `.git/`, `.claude/`, `.idea/`, `.vscode/`, `dist/`, `build/`, `coverage/`, `instance/`, `*.db`, `*.sqlite`, `*.lock`, `package-lock.json`, `yarn.lock`, binários e imagens.

"Source files" = arquivos de código da aplicação (incluindo seeds/scripts), **sem** manifestos, READMEs e `__init__.py` vazios. Conte linhas com `wc -l` (ou equivalente) e informe o total aproximado.

## 2. Detecção de linguagem

| Evidência | Linguagem |
|---|---|
| `*.py`, `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile` | Python |
| `*.js`/`*.mjs`/`*.cjs` + `package.json` | JavaScript (Node.js) |
| `*.ts` + `tsconfig.json` | TypeScript (Node.js) |
| `*.java` + `pom.xml`/`build.gradle` | Java |
| `*.go` + `go.mod` | Go |
| `*.rb` + `Gemfile` | Ruby |
| `*.php` + `composer.json` | PHP |
| `*.cs` + `*.csproj` | C# |

A linguagem predominante é a de maior número de linhas de código da aplicação. Informe a versão quando declarada (`engines` no `package.json`, `python_requires`, `.python-version`, `.nvmrc`) ou, na falta, a do runtime instalado (`python --version`, `node --version`) marcando como "runtime local".

## 3. Detecção de framework

Leia a versão **do manifesto** (ex.: `flask==3.1.1` → "Flask 3.1.1"; `"express": "^4.18.2"` → "Express 4.18.2 (^4)").

| Sinal no manifesto | Sinal no código | Framework |
|---|---|---|
| `flask` | `Flask(__name__)`, `@app.route`, `Blueprint`, `add_url_rule` | Flask |
| `django` | `settings.py`, `urls.py`, `INSTALLED_APPS` | Django |
| `fastapi` | `FastAPI()`, `@app.get`, `APIRouter` | FastAPI |
| `express` | `express()`, `app.get/post`, `express.Router()` | Express |
| `@nestjs/core` | `@Controller`, `@Module` | NestJS |
| `fastify` / `koa` / `hapi` | `fastify()`, `new Koa()` | Fastify / Koa / Hapi |
| `spring-boot-starter-web` | `@RestController` | Spring Boot |
| `gin-gonic/gin`, `labstack/echo` | `gin.Default()` | Gin / Echo |
| `rails` / `sinatra` | `config/routes.rb` | Rails / Sinatra |
| `laravel/framework` | `routes/web.php` | Laravel |

Dependências relevantes = as que afetam a arquitetura: ORM/driver de banco, CORS, validação (marshmallow, pydantic, joi, zod), auth (jwt, bcrypt), HTTP clients, mail, dotenv.

## 4. Detecção de banco de dados e acesso a dados

| Sinal | Banco / forma de acesso |
|---|---|
| `import sqlite3`, `sqlite3.connect(...)` | SQLite via SQL cru (driver DB-API) |
| `require('sqlite3')`, `new sqlite3.Database(':memory:')` | SQLite via SQL cru (callbacks); `:memory:` = volátil, seeds no boot |
| `flask_sqlalchemy`, `db.Model`, `SQLALCHEMY_DATABASE_URI` | ORM SQLAlchemy (engine pela URI) |
| `psycopg2`, `pg`, `postgres://` | PostgreSQL |
| `mysql`, `mysql2`, `pymysql` | MySQL |
| `mongoose`, `pymongo`, `mongodb://` | MongoDB |
| `sequelize`, `typeorm`, `prisma`, `knex` | ORM/query builder Node |

**Tabelas/entidades:** extraia de `CREATE TABLE`, `__tablename__`, classes `db.Model`, schemas Mongoose, `model` do Prisma. Anote também onde o schema é criado (no boot? em migração? em seed?) e se há seed automático — isso importa para a validação da Fase 3.

## 5. Inferência de domínio

Derive o domínio dos **nomes de tabelas/entidades e rotas**, não do nome da pasta:
- `produtos`, `pedidos`, `itens_pedido`, `usuarios` → E-commerce (catálogo, pedidos, usuários)
- `courses`, `enrollments`, `payments` + rota `/checkout` → LMS / plataforma de cursos com checkout
- `tasks`, `categories`, `users` + `/reports` → Task Manager / gestão de tarefas

Descreva em uma linha: `<tipo de sistema> (<entidades principais>)`.

## 6. Classificação da arquitetura atual

| Padrão observado | Classificação |
|---|---|
| 1–4 arquivos; rotas, SQL e regra de negócio misturados; sem pastas de camada | **Monolítica — sem separação de camadas** |
| Uma classe/arquivo "manager" que cria o banco, define rotas e processa regras | **Monolítica — God Class (<Nome>)** |
| Arquivos nomeados `models.py`/`controllers.py` mas o "model" contém regra de negócio e o "controller" faz validação + notificações | **Pseudo-camadas (nomes MVC, responsabilidades misturadas)** |
| Pastas `routes/`, `models/`, `services/`, `utils/` mas regra de negócio dentro das rotas e services subutilizados | **Camadas parciais — rotas gordas** |
| Separação clara routes → controllers → models, config isolada, error handler central | **MVC / em camadas (já adequado)** |

Justifique a classificação citando 1–2 evidências (ex.: "SQL em `models.py` e regras de desconto em `models.py:256`").

## 7. Entry point e execução

- Python: arquivo com `if __name__ == "__main__":` / `app.run(...)`, ou factory `create_app()`; porta em `app.run(port=...)`.
- Node: `main` e `scripts.start` do `package.json`; `app.listen(...)`.
- Confirme com o README do projeto ("Como rodar"). Registre também scripts auxiliares obrigatórios (ex.: `python seed.py` antes do primeiro boot).

## 8. Inventário de endpoints

Encontre todas as rotas:

| Stack | Busca |
|---|---|
| Flask | `@app.route`, `@<bp>.route`, `add_url_rule(`, `register_blueprint` (prefixos!) |
| FastAPI | `@app.get/post/put/delete/patch`, `@router.*`, `include_router(prefix=)` |
| Django | `path(`, `re_path(` em `urls.py` |
| Express | `app.get/post/put/delete/patch(`, `router.*(`, `app.use('/prefix', router)` |

Para cada uma: método, caminho completo (com prefixo), handler, arquivo:linha, e se exige body (campos lidos do request). Rotas com o mesmo caminho e métodos diferentes contam separadamente. Atenção à ordem de declaração quando há rotas estáticas vs. dinâmicas (`/produtos/busca` vs `/produtos/<id>`) — a ordem precisa ser preservada na refatoração.
