# Catálogo de Anti-patterns (Fase 2)

Cada entrada traz: **severidade padrão**, **sinais de detecção** (textuais → use Grep; estruturais → leia o código), **falsos positivos** a descartar e o **padrão do playbook** que corrige.

## Escala de severidade

- **CRITICAL** — falha grave de segurança ou arquitetura: expõe dados sensíveis (credenciais hardcoded, SQL Injection, execução arbitrária), ou viola completamente a separação de responsabilidades (God Class com banco + regra + roteamento).
- **HIGH** — forte violação de MVC/SOLID que dificulta muito manutenção e testes: regra de negócio pesada em controllers/rotas, acoplamento forte sem injeção de dependência, estado global mutável, integridade de dados comprometida.
- **MEDIUM** — padronização, duplicação, performance moderada: N+1, validação ausente/duplicada, error handling espalhado, middleware inadequado, APIs deprecated.
- **LOW** — legibilidade: nomes ruins, magic numbers, prints de debug, imports não usados, condicionais verbosas.

**Ajuste de severidade:** suba um nível quando o problema estiver num caminho crítico (auth, pagamento, endpoint público) ou se combinar com outro (ex.: `debug=True` + `host=0.0.0.0`); desça um nível quando estiver restrito a script de seed/dev. Justifique ajustes na descrição.

## Índice

| ID | Anti-pattern | Severidade padrão |
|---|---|---|
| AP-01 | Credenciais e segredos hardcoded | CRITICAL |
| AP-02 | SQL Injection (query por concatenação/interpolação) | CRITICAL |
| AP-03 | God Class / God Module | CRITICAL |
| AP-04 | Endpoint perigoso sem proteção (execução arbitrária, reset, admin aberto) | CRITICAL |
| AP-05 | Exposição de dados sensíveis (respostas e logs) | CRITICAL |
| AP-06 | Armazenamento inseguro de senha (texto puro, MD5/SHA1, cripto caseira) | CRITICAL / HIGH |
| AP-07 | Regra de negócio em controllers/rotas (Fat Controller) | HIGH |
| AP-08 | Estado global mutável / conexão singleton global | HIGH |
| AP-09 | Acoplamento forte sem injeção de dependência | HIGH |
| AP-10 | Callback Hell / fluxo assíncrono sem propagação de erro | HIGH |
| AP-11 | Escrita múltipla sem transação / integridade referencial quebrada | HIGH |
| AP-12 | Configuração insegura de runtime (debug em produção, CORS aberto) | HIGH |
| AP-13 | Queries N+1 | MEDIUM |
| AP-14 | Validação de entrada ausente, inconsistente ou duplicada | MEDIUM |
| AP-15 | Error handling não centralizado / `except` genérico / vazamento de erro | MEDIUM |
| AP-16 | Duplicação de código (serialização, regras, constantes) | MEDIUM |
| AP-17 | Uso de APIs deprecated | MEDIUM |
| AP-18 | Magic numbers e strings | LOW |
| AP-19 | Nomenclatura ruim | LOW |
| AP-20 | `print`/`console.log` como logging | LOW |
| AP-21 | Imports não usados e código morto | LOW |
| AP-22 | Condicionais verbosas / aninhamento desnecessário | LOW |

---

## AP-01 — Credenciais e segredos hardcoded — CRITICAL

**Sinais textuais (Grep, case-insensitive):**
`SECRET_KEY\s*=|secret|password\s*[:=]\s*['"]|passwd|pwd\s*[:=]|api[_-]?key|token\s*[:=]\s*['"]|pk_live|sk_live|smtp.*(user|pass)|dbPass|dbUser|DATABASE_URL\s*=\s*['"]`
**Sinais estruturais:** objeto/dicionário `config` com valores literais de senha/chave; atributos de classe como `self.email_password = '...'`; URIs de banco com usuário:senha.
**Falsos positivos:** valores lidos de `os.environ`/`process.env` sem default sensível; placeholders em `.env.example`; senhas de usuários **de seed** (essas entram em AP-06 se ficarem em texto puro).
**Impacto:** qualquer pessoa com acesso ao repositório obtém chaves de produção; rotação exige deploy.
**Playbook:** PB-01.

## AP-02 — SQL Injection — CRITICAL

**Sinais textuais:**
- Python: `execute\(.*["'] *\+|execute\(f["']|execute\(.*%\s*\(|execute\(.*\.format\(`; variáveis `query += " AND ... '" + x`
- Node: `` (db\.(run|get|all|query|exec))\(`[^`]*\$\{ `` ou `"... " + req.`
- Qualquer: `LIKE '%" + termo + "%'`
**Sinais estruturais:** valores vindos do request chegam a uma string SQL sem placeholder (`?`, `%s`, `:nome`, `$1`).
**Falsos positivos:** concatenação apenas de constantes internas (nomes de coluna de uma whitelist); ORMs com filtros (`filter_by`, `.like(f'%{q}%')` do SQLAlchemy é parametrizado — não é injection).
**Impacto:** leitura/alteração/destruição arbitrária do banco, bypass de login (`' OR '1'='1`).
**Playbook:** PB-02. Liste **todas** as linhas afetadas no mesmo finding.

## AP-03 — God Class / God Module — CRITICAL

**Sinais estruturais:**
- Um arquivo/classe contém ≥ 3 destes papéis: conexão/criação de schema, SQL/ORM, regra de negócio, roteamento HTTP, validação, formatação de resposta, notificações.
- Classe "Manager"/"Helper"/"Utils" com métodos `initDb` + `setupRoutes` + lógica de pagamento.
- Arquivo `models.py`/`controllers.py` cobrindo ≥ 3 domínios diferentes (produtos, usuários, pedidos, relatórios) com > ~250 linhas.
- Funções > ~50 linhas fazendo múltiplas coisas (God Method).
**Impacto:** impossível testar em isolamento; qualquer mudança afeta tudo; viola SRP.
**Playbook:** PB-03 (+ PB-04 para regra de negócio).

## AP-04 — Endpoint perigoso sem proteção — CRITICAL

**Sinais:** rotas `/admin/*`, `/reset`, `/query`, `/exec`, `/debug`, relatórios financeiros, `DELETE` de usuários, sem nenhum middleware/decorator de autenticação/autorização; `cursor.execute(request...)`, `eval`, `exec`, `child_process` com dados do request.
**Impacto:** execução de SQL arbitrário, destruição de dados, vazamento de informação financeira.
**Playbook:** PB-09 (proteger com auth/flag de ambiente; preservar a rota respondendo 401/403 em vez de removê-la silenciosamente).

## AP-05 — Exposição de dados sensíveis — CRITICAL

**Sinais:**
- Serialização inclui `senha`/`password`/`pass`/hash (`to_dict` com `'password'`, `SELECT *` devolvido direto ao cliente).
- Endpoints de health/debug que retornam `secret_key`, `db_path`, flags de debug.
- Logs com número de cartão, senha, chave de API: `console.log(\`...${cc}...${config.paymentGatewayKey}\`)`, `print("... " + senha)`.
- Tokens falsos/previsíveis (`'fake-jwt-token-' + id`) usados como autenticação (HIGH se não houver uso real).
**Playbook:** PB-09 (serialização por whitelist), PB-15 (logging sem dados sensíveis).

## AP-06 — Armazenamento inseguro de senha — CRITICAL (texto puro) / HIGH (hash fraco)

**Sinais:** `INSERT ... senha` com valor cru; comparação `WHERE senha = ?` direta; `hashlib.md5`, `hashlib.sha1`, `sha256` sem salt; funções caseiras (`badCrypto`, base64 repetido); `crypto.createHash('md5')`.
**Impacto:** vazamento do banco expõe todas as senhas (rainbow tables).
**Playbook:** PB-08 (werkzeug/bcrypt/argon2; Node: `bcrypt`/`crypto.scrypt`). Atualize seeds para gerar hashes e garanta que o login com as credenciais de seed continua funcionando.

## AP-07 — Fat Controller / regra de negócio na rota — HIGH

**Sinais estruturais:**
- Handler HTTP com > ~30 linhas, cálculos (descontos, totais, estatísticas), loops sobre dados, várias consultas ao banco, decisões de status.
- "Model" que calcula descontos/faturamento (regra de negócio no lugar errado também conta).
- Efeitos colaterais de negócio (enviar e-mail/SMS/push, baixar estoque) dentro da rota.
**Playbook:** PB-04.

## AP-08 — Estado global mutável — HIGH

**Sinais:** `global db_connection`; variáveis de módulo mutadas (`globalCache = {}`, `totalRevenue = 0`, `notifications = []` em singleton); conexão criada no import; `check_same_thread=False` compartilhando uma conexão entre threads.
**Impacto:** condições de corrida, testes que interferem entre si, impossível trocar implementação.
**Playbook:** PB-06.

## AP-09 — Acoplamento forte sem injeção de dependência — HIGH

**Sinais:** controllers/rotas que importam e chamam o driver do banco direto (`get_db()` no controller); classes que instanciam suas dependências no construtor (`new sqlite3.Database(...)`, `smtplib.SMTP(...)` dentro do service); módulos de rota importando todos os models e fazendo queries; ausência de composition root.
**Playbook:** PB-06.

## AP-10 — Callback Hell / async sem propagação de erro — HIGH

**Sinais (Node):** ≥ 3 níveis de callbacks aninhados; contadores manuais de pendências (`pending--; if (pending === 0) res.json(...)`); callbacks que ignoram `err` (`(err, row) => { ... }` sem checar `err`); `function(err) { this.lastID }` misturado com `self`.
**Sinais (Python):** threads/callbacks manuais sem tratamento de erro.
**Playbook:** PB-10 (promisificar repositório + `async/await` + `try/catch` → error handler).

## AP-11 — Escrita múltipla sem transação / integridade quebrada — HIGH

**Sinais:** sequência de `INSERT`/`UPDATE` relacionados (pedido + itens + baixa de estoque; matrícula + pagamento) sem `BEGIN/COMMIT/ROLLBACK`; `return` de erro no meio do loop após já ter escrito; `DELETE` de entidade pai deixando filhos órfãos (comentários ou respostas admitindo "dados sujos"); FKs sem `ON DELETE`.
**Playbook:** PB-11.

## AP-12 — Configuração insegura de runtime — HIGH

**Sinais:** `debug=True`/`app.config["DEBUG"] = True` fixo (com `host="0.0.0.0"` o debugger Werkzeug permite RCE → suba para CRITICAL); `CORS(app)` sem origens; porta/host fixos no código; `ambiente: "producao"` literal.
**Playbook:** PB-01.

## AP-13 — Queries N+1 — MEDIUM

**Sinais:** query dentro de `for`/`forEach` sobre resultados de outra query (`cursor.execute` / `Model.query.get` / `db.get` no loop); acesso a relacionamento lazy dentro de loop (`len(u.tasks)`, `t.user.name`); contagens por status em N queries separadas (`filter_by(status='x').count()` repetido) quando um `GROUP BY` resolve.
**Playbook:** PB-07.

## AP-14 — Validação ausente, inconsistente ou duplicada — MEDIUM

**Sinais:** `request.get_json()`/`req.body` usado sem checar `None`/tipo; comparação numérica com valor possivelmente string (`priority < 1` com JSON string → `TypeError` 500); mesmas regras repetidas em create e update (e divergentes); lista de valores válidos repetida em vários arquivos; helper de validação existente mas não usado; ausência de verificação de unicidade (e-mail).
**Playbook:** PB-12.

## AP-15 — Error handling não centralizado — MEDIUM

**Sinais:** `try/except Exception as e: return jsonify({"erro": str(e)}), 500` repetido em todo handler; `except:` nu (engole `KeyboardInterrupt`/erros de programação); `str(e)` enviado ao cliente (vaza detalhes internos); respostas de erro com formatos diferentes (`erro` vs `error`, texto puro vs JSON); ausência de `@app.errorhandler`/middleware de erro do Express.
**Playbook:** PB-05.

## AP-16 — Duplicação de código — MEDIUM

**Sinais:** mesmo bloco de serialização (dict campo a campo) repetido em ≥ 2 lugares mesmo existindo `to_dict()`; mesma regra (ex.: "tarefa atrasada") reimplementada em vários arquivos apesar de existir método no model; funções de listagem quase idênticas (`get_pedidos_usuario` vs `get_todos_pedidos`).
**Playbook:** PB-16.

## AP-17 — APIs deprecated — MEDIUM (LOW se apenas aviso cosmético)

Verifique contra as versões do manifesto **e** do runtime local. Cada uso vira localização do finding; recomende o equivalente moderno.

| Stack | Deprecated / legado | Substituto moderno |
|---|---|---|
| Python ≥ 3.12 | `datetime.utcnow()`, `datetime.utcfromtimestamp()` | `datetime.now(timezone.utc)` (se o banco guarda datetimes *naive*, use `datetime.now(timezone.utc).replace(tzinfo=None)` para não quebrar comparações) |
| SQLAlchemy ≥ 2.0 / Flask-SQLAlchemy ≥ 3 | `Model.query.get(id)` (legacy Query API) | `db.session.get(Model, id)` |
| SQLAlchemy ≥ 2.0 | `Model.query.filter_by(...).all()` (legacy, ainda suportado) | `db.session.execute(db.select(Model).filter_by(...)).scalars().all()` — recomende, migre se o projeto já usa SQLAlchemy 2 |
| Flask ≥ 2.3 | `@app.before_first_request`, `flask.json.JSONEncoder`, `app.json_encoder` | lógica no `create_app()`; `app.json` provider |
| Flask | `app.config['DEBUG']` como controle de debug | `FLASK_DEBUG`/config por ambiente |
| Python | `hashlib.md5` para senha | `werkzeug.security.generate_password_hash` / `bcrypt` (também AP-06) |
| Python | `distutils`, `imp`, `pkg_resources`, `asyncio.get_event_loop()` fora de loop | `setuptools`/`packaging`, `importlib`, `importlib.metadata`, `asyncio.run` |
| Python | `type(x) == list` | `isinstance(x, list)` (estilo; LOW) |
| Node | `new Buffer(x)` | `Buffer.from(x)` |
| Node | `url.parse()`, `querystring` | `new URL()`, `URLSearchParams` |
| Node | `fs.exists`, `util.isArray` etc. | `fs.existsSync`/`fs.promises.access`, `Array.isArray` |
| Express 4→5 | `req.param()`, `res.send(status, body)`, `res.json(status, obj)`, `app.del`, `res.sendfile` | `req.params/query/body`, `res.status(s).send(b)`, `app.delete`, `res.sendFile` |
| Express | `body-parser` como pacote separado | `express.json()` / `express.urlencoded()` |
| Node sqlite3 | API de callbacks sem promisificação | wrapper com `util.promisify`/Promises + `async/await` (ou `better-sqlite3`) |
| JS | `var` | `const`/`let` (LOW) |

Se nenhuma API deprecated for encontrada, registre no relatório: "Nenhuma API deprecated detectada nas versões X/Y."
**Playbook:** PB-13.

## AP-18 — Magic numbers e strings — LOW

**Sinais:** limiares numéricos em regras (`> 10000`, `* 0.1`, `<= 2`, `len(x) < 3`, `10000` iterações); status literais repetidos (`'pendente'`, `'PAID'`, `'done'`); prefixo de cartão `startsWith("4")`; portas e cores literais.
**Playbook:** PB-14.

## AP-19 — Nomenclatura ruim — LOW

**Sinais:** variáveis de 1–3 letras fora de loops curtos (`u`, `e`, `p`, `cid`, `cc`); campos de API abreviados (`usr`, `eml`, `pwd`, `c_id`) — **renomeie internamente, mas preserve os nomes externos do contrato**; nomes que mentem (`badCrypto`, `AppManager`, `utils` contendo config); sombreamento de builtins (`id`, `type`).
**Playbook:** PB-14 (seção nomenclatura).

## AP-20 — `print`/`console.log` como logging — LOW

**Sinais:** `print(` / `console.log(` em código de aplicação para eventos, erros ou "simular" envio de e-mail/SMS. (Sobe para CRITICAL/AP-05 se logar dados sensíveis.)
**Playbook:** PB-15.

## AP-21 — Imports não usados e código morto — LOW

**Sinais:** imports nunca referenciados (`import os, sys, json, time` sem uso; `import sqlite3` sem uso); funções/constantes definidas e nunca chamadas (`generate_id`, `VALID_ROLES` não usados); variáveis exportadas sem uso (`totalRevenue`); métodos de validação no model ignorados pelas rotas.
**Detecção:** para cada import/def, Grep pelo nome no projeto.
**Playbook:** PB-16 (remoção) / PB-12 (passar a usar validações existentes).

## AP-22 — Condicionais verbosas — LOW

**Sinais:** `if cond: return True else: return False`; `if x: if y: if z:` aninhados que viram uma expressão booleana; `len(lista) == 0` após `not lista`.
**Playbook:** PB-14.

---

## Checklist de varredura

Para cada arquivo-fonte, responda: tem segredo literal? SQL montado com dados externos? Quantos papéis (DB, regra, HTTP, validação, notificação) ele acumula? Há query em loop? Há escrita múltipla sem transação? Como os erros são tratados? Quais APIs estão deprecated para as versões em uso? Há literais mágicos, prints, imports sem uso? Só depois passe ao próximo arquivo.

Meta mínima do relatório: ≥ 5 findings e ≥ 1 CRITICAL ou HIGH — em projetos legados isso costuma ser amplamente superado; se não atingir, revise o checklist antes de concluir.
