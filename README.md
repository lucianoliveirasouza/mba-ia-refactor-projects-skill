# Refatoração Arquitetural Automatizada com Skills — `refactor-arch`

Entrega do desafio **"Criação de Skills — Refatoração Arquitetural Automatizada"** (MBA IA).

Foi construída uma skill do **Claude Code** (`.claude/skills/refactor-arch/`) que, em 3 fases sequenciais, **analisa** a stack de um projeto backend, **audita** anti-patterns com severidade e localização exata e, após confirmação humana, **refatora** o projeto para MVC **validando** que a aplicação continua de pé. A mesma skill (sem nenhuma alteração) foi executada nos 3 projetos legados do repositório — dois em Python/Flask e um em Node.js/Express.

| Entregável | Local |
|---|---|
| Skill completa | `code-smells-project/.claude/skills/refactor-arch/` (cópias idênticas em `ecommerce-api-legacy/` e `task-manager-api/`) |
| Código refatorado | `code-smells-project/`, `ecommerce-api-legacy/`, `task-manager-api/` |
| Relatórios de auditoria (saída da Fase 2) | `reports/audit-project-1.md`, `reports/audit-project-2.md`, `reports/audit-project-3.md` |
| Logs completos das execuções | `reports/logs/project-{1,2,3}-phase-{1-2,3}.log` |

---

## A) Análise Manual

Antes de escrever a skill, li integralmente o código dos 3 projetos. Abaixo, os problemas que considerei de maior impacto (severidade segundo a escala do desafio). Esses achados viraram os sinais de detecção do catálogo da skill.

### Projeto 1 — `code-smells-project` (Python/Flask, E-commerce)

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | **SQL Injection** — praticamente todas as queries são montadas por concatenação, inclusive o login (`"... WHERE email = '" + email + "' AND senha = '" + senha + "'"`) | `models.py:28, 47-50, 109-111, 289-297` | Permite bypass de login com `' OR '1'='1` e leitura/alteração arbitrária do banco. |
| 2 | CRITICAL | **Endpoint de SQL arbitrário e reset do banco sem autenticação** (`POST /admin/query` executa o SQL do body; `POST /admin/reset-db` apaga tudo) | `app.py:47-78` | Qualquer cliente anônimo destrói ou extrai o banco inteiro. |
| 3 | CRITICAL | **Segredos hardcoded e vazados** — `SECRET_KEY` literal, devolvida também no `/health`; `debug=True` com `host=0.0.0.0` | `app.py:7-8, 88`, `controllers.py:289` | Chave de sessão exposta publicamente e debugger Werkzeug (RCE) acessível na rede. |
| 4 | CRITICAL | **Senhas em texto puro e expostas na API** — seed grava `admin123`; `GET /usuarios` devolve o campo `senha` | `database.py:75-83`, `models.py:83, 99` | Um GET público vaza as credenciais de todos os usuários. |
| 5 | HIGH | **Conexão SQLite global mutável** (`global db_connection`, `check_same_thread=False`) | `database.py:4-11` | Estado compartilhado entre threads; escritas parciais de uma requisição podem ser commitadas por outra. |
| 6 | HIGH | **Regra de negócio no lugar errado** — o "model" calcula faixas de desconto e estoque; o "controller" valida, notifica e faz SQL | `models.py:133-169, 256-262`, `controllers.py:24-62` | Nomes MVC com responsabilidades misturadas: impossível testar regras isoladamente. |
| 7 | MEDIUM | **Queries N+1** na listagem de pedidos (1 query por pedido + 1 por item) | `models.py:187-193, 219-225` | Custo cresce com pedidos × itens. |
| 8 | MEDIUM | **Error handling duplicado** — `except Exception as e: return jsonify({"erro": str(e)}), 500` em todos os handlers | `controllers.py` (16 ocorrências) | Vaza detalhes internos ao cliente e duplica código. |
| 9 | LOW | **Magic numbers** — faixas de desconto `10000/5000/1000` e `0.1/0.05/0.02`, listas de status/categorias inline | `models.py:257-262`, `controllers.py:52, 242` | Regras de negócio escondidas em literais. |
| 10 | LOW | **`print` como logging** e para "simular" e-mail/SMS | `controllers.py:208-210` e outros | Sem níveis, sem controle em produção. |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, LMS com checkout)

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | **Credenciais de produção hardcoded** (`dbPass`, `paymentGatewayKey: "pk_live_..."`) | `src/utils.js:1-7` | Quem lê o repositório obtém a chave de pagamento live. |
| 2 | CRITICAL | **Número do cartão e chave do gateway em log** (`console.log(\`Processando cartão ${cc} na chave ${...}\`)`) | `src/AppManager.js:45` | Vazamento de PAN (PCI-DSS) e da chave em qualquer agregador de logs. |
| 3 | CRITICAL | **God Class `AppManager`** — cria o banco, o schema, o seed, registra as rotas e processa pagamento | `src/AppManager.js:4-139` | Viola completamente a separação de responsabilidades. |
| 4 | CRITICAL | **"Criptografia" caseira de senha** (`badCrypto`: base64 truncado, sem salt) e senha padrão `123456` | `src/utils.js:17-23`, `src/AppManager.js:68` | Hash reversível/colidível; contas criadas com senha previsível. |
| 5 | HIGH | **Callback hell sem tratamento de erro** — até 6 níveis, contadores manuais, `err` ignorado | `src/AppManager.js:37-77, 83-128` | Exceções em callbacks derrubam o processo; requisições podem nunca responder. |
| 6 | HIGH | **Checkout sem transação** e `DELETE` de usuário deixando matrículas/pagamentos órfãos (a própria resposta admite "dados sujos") | `src/AppManager.js:50-61, 131-137` | Inconsistência de dados financeiros. |
| 7 | MEDIUM | **N+1 no relatório financeiro** (1 + cursos + 2 × matrículas queries) | `src/AppManager.js:89-106` | Degrada linearmente com o volume. |
| 8 | MEDIUM | **Validação de entrada ausente** — `card` numérico faz `cc.startsWith` lançar TypeError e derrubar o servidor | `src/AppManager.js:29-35, 46` | DoS trivial por payload malformado. |
| 9 | LOW | **Nomenclatura ruim** — `u`, `e`, `p`, `cid`, `cc`, `self`, `badCrypto`, `AppManager` | `src/AppManager.js:29-33` | Nomes não revelam intenção. |
| 10 | LOW | **Código morto / estado global inútil** — `globalCache` só escrito, `totalRevenue` nunca usado | `src/utils.js:9-15, 25` | Vazamento de memória e falsa funcionalidade. |

### Projeto 3 — `task-manager-api` (Python/Flask, Task Manager com camadas parciais)

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | **Senhas com MD5 sem salt** | `models/user.py:27-32` | MD5 é quebrável por rainbow tables em segundos. |
| 2 | CRITICAL | **Hash de senha devolvido nas respostas** (`to_dict()` inclui `password`, usado em `POST /users`, `GET /users/<id>` e no `/login`) | `models/user.py:16-25` | Vaza o hash de todos os usuários. |
| 3 | CRITICAL | **Credenciais hardcoded** — `SECRET_KEY`, senha SMTP `senha123` no `NotificationService` | `app.py:13`, `services/notification_service.py:7-10` | Segredos no repositório. |
| 4 | HIGH | **Rotas gordas** — estatísticas, regra de "atrasada" e validações inteiras dentro das rotas; `services/` e `utils/` quase não usados | `routes/report_routes.py:12-101`, `routes/task_routes.py:11-63` | A separação em pastas existe, mas a responsabilidade não. |
| 5 | HIGH | **Token de autenticação falso** (`'fake-jwt-token-' + id`) e qualquer um pode se cadastrar como `admin` | `routes/user_routes.py:52, 210` | Escalonamento de privilégio trivial. |
| 6 | MEDIUM | **N+1** — `User.query.get`/`Category.query.get` por task; contagens por status em N queries | `routes/task_routes.py:41-57`, `routes/report_routes.py:15-28, 53-68` | Muitas queries por requisição. |
| 7 | MEDIUM | **APIs deprecated** — `datetime.utcnow()` (Python ≥ 3.12) e `Model.query.get()` (SQLAlchemy 2.0 legacy) | `models/*.py`, `routes/*.py` | Avisos hoje, quebra em versões futuras. |
| 8 | MEDIUM | **Duplicação** — a regra "overdue" reimplementada em 5 lugares apesar de existir `Task.is_overdue()`; serialização campo a campo repetida | `routes/task_routes.py:30-39, 71-80`, `routes/user_routes.py:171-180` | Mudança de regra exige editar vários arquivos. |
| 9 | LOW | **Imports não usados** (`import os, sys, json, time`, `hashlib`, `re`…) | `app.py:7`, `routes/task_routes.py:7`, `utils/helpers.py:3-7` | Ruído. |
| 10 | LOW | **Condicionais verbosas** (`if ...: return True else: return False`) e magic numbers (prioridade `1..5`, tamanho mínimo `3`, senha `4`) | `models/task.py:38-60`, `models/user.py:34-38` | Legibilidade. |

---

## B) Construção da Skill

### Estrutura

```
.claude/skills/refactor-arch/
├── SKILL.md                          # o "prompt": workflow das 3 fases, regras e formatos de saída
└── references/
    ├── project-analysis.md           # Área 1 — heurísticas de detecção de linguagem/framework/banco/arquitetura
    ├── anti-patterns-catalog.md      # Área 2 — 22 anti-patterns com sinais de detecção e severidade (inclui APIs deprecated)
    ├── audit-report-template.md      # Área 3 — formato padronizado do relatório da Fase 2
    ├── mvc-guidelines.md             # Área 4 — camadas, responsabilidades, direção de dependências, estruturas alvo por stack
    └── refactoring-playbook.md       # Área 5 — 16 padrões de transformação com código antes/depois
```

### Decisões de design

- **SKILL.md como orquestrador, referências como conhecimento.** O `SKILL.md` só define *o que fazer e em que ordem* (fases, gates, formatos de saída); todo o conhecimento de domínio fica nos arquivos de referência, carregados **sob demanda no início de cada fase** (progressive disclosure), o que mantém o contexto enxuto.
- **Gate rígido entre auditoria e refatoração.** A Fase 2 é estritamente somente leitura — **nem o relatório é gravado** antes da resposta `[y/n]`; após a resposta ele é salvo e, se `y`, começa a Fase 3. O caminho do relatório pode ser passado como argumento (`/refactor-arch ../reports/audit-project-1.md`).
- **Evidência obrigatória.** Todo finding precisa de `arquivo:linha` conferido lendo o arquivo; ocorrências da mesma causa são agrupadas em um finding com várias localizações.
- **Validação por baseline.** Antes de editar qualquer arquivo, a Fase 3 sobe a aplicação **original**, chama todos os endpoints do inventário da Fase 1 e guarda status + chaves das respostas. Depois da refatoração repete as chamadas e compara. Isso transforma "os endpoints continuam respondendo" num teste objetivo.
- **Contrato preservado.** Rotas, métodos, nomes de campos, porta e comando de execução são mantidos; a única exceção aceita é correção de segurança (ex.: não devolver hash de senha, exigir token em rota admin), sempre listada na seção *Contract Changes* do resumo final.
- **Sem commits pela skill.** O humano decide o que commitar.

### Anti-patterns do catálogo (e por quê)

| Severidade | Anti-patterns | Motivação |
|---|---|---|
| CRITICAL | AP-01 Segredos hardcoded · AP-02 SQL Injection · AP-03 God Class · AP-04 Endpoint perigoso sem proteção · AP-05 Exposição de dados sensíveis · AP-06 Senha insegura | Os exemplos da própria definição de CRITICAL do desafio, todos presentes nos projetos (SQL livre, `pk_live` em código, cartão em log, MD5). |
| HIGH | AP-07 Fat Controller · AP-08 Estado global · AP-09 Acoplamento sem DI · AP-10 Callback hell · AP-11 Escrita sem transação · AP-12 Config insegura de runtime | Violações de MVC/SOLID que travam teste e manutenção; AP-10 é essencial para cobrir Node. |
| MEDIUM | AP-13 N+1 · AP-14 Validação ausente/duplicada · AP-15 Error handling espalhado · AP-16 Duplicação · **AP-17 APIs deprecated** | Problemas de padronização/performance; AP-17 traz uma tabela *deprecated → moderno* para Python, Flask, SQLAlchemy, Node e Express. |
| LOW | AP-18 Magic numbers · AP-19 Nomenclatura · AP-20 `print` como log · AP-21 Código morto · AP-22 Condicionais verbosas | Legibilidade. |

Cada entrada traz **sinais textuais** (regex para Grep, ex.: `execute\(.*["'] *\+`), **sinais estruturais** (ex.: "query dentro de `for` sobre o resultado de outra query"), **falsos positivos** a descartar (ex.: `.like(f'%{q}%')` do SQLAlchemy é parametrizado) e o **padrão do playbook** que corrige.

### Como a skill ficou agnóstica de tecnologia

- **Detecta, não assume:** a Fase 1 usa tabelas de evidência (manifesto + sinais no código) para Python, Node/TS, Java, Go, Ruby, PHP e C#, e frameworks Flask, Django, FastAPI, Express, NestJS, Fastify, Spring, Gin, Rails, Laravel.
- **Sinais de detecção por conceito**, com variantes por linguagem (ex.: SQL Injection cobre concatenação Python, f-string, template literal JS).
- **Estruturas alvo por stack e por nível de organização:** Flask monolítico (`src/` com camadas), Flask com camadas parciais (evoluir as pastas existentes, criando `controllers/`) e Express (`src/` com `routes/controllers/models/middlewares`).
- **Playbook com exemplos nas duas stacks** e instrução explícita de adaptar ao idioma dos nomes do projeto (ex.: `produto_model.py`).
- **Validação genérica**: o comando de execução e o seed vêm do README/manifesto; a validação usa `curl` sobre o inventário de endpoints, independente do framework.

### Desafios encontrados e como foram resolvidos

| Desafio | Solução |
|---|---|
| "Pedir confirmação antes de modificar qualquer arquivo" conflitava com "salvar o relatório da Fase 2" | A Fase 2 só imprime; o relatório é gravado como primeira ação **após** a resposta do usuário (qualquer que seja). |
| Garantir que "os endpoints continuam respondendo" fosse verificável e não só declarado | Baseline do comportamento original capturada antes de qualquer edição e comparada depois (status + chaves de primeiro nível). |
| Correções de segurança necessariamente mudam respostas (ex.: tirar `senha` do JSON) | Regra explícita de "contrato preservado, exceto segurança", com seção *Contract Changes* obrigatória no resumo final. |
| Rotas destrutivas (`/admin/query`, `DELETE /users`) precisam ser protegidas, mas removê-las quebraria o contrato | Playbook PB-09: manter a rota respondendo, protegida por token de ambiente (401/403 sem credencial). |
| Projeto parcialmente organizado (task-manager) poderia ser "recriado do zero" | Seção específica no guideline: evoluir pastas existentes, extrair regra das rotas para `controllers/`, reaproveitar models/services. |
| `datetime.utcnow()` → `datetime.now(timezone.utc)` quebra comparações com datetimes *naive* gravados no SQLite | Playbook PB-13 recomenda `datetime.now(timezone.utc).replace(tzinfo=None)` para manter compatibilidade. |
| Execução headless (`claude -p`) e a pausa da Fase 2 | Primeira chamada executa Fases 1–2 e para no `[y/n]`; a resposta é enviada com `claude -p --continue "y"`, retomando a mesma sessão. |
| O validador genérico do `skill-creator` rejeitava o campo `argument-hint` | Campo removido do frontmatter (só `name` e `description`), tornando a skill portável; o argumento continua disponível via `$ARGUMENTS`. |

---

## C) Resultados

### Resumo das auditorias (Fase 2)

| Projeto | Stack detectada | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
|---|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python + Flask 3.1.1 | 7 | 4 | 4 | 6 | **21** | [audit-project-1.md](reports/audit-project-1.md) |
| 2 — ecommerce-api-legacy | Node.js + Express 4.22.1 | 5 | 5 | 5 | 4 | **19** | [audit-project-2.md](reports/audit-project-2.md) |
| 3 — task-manager-api | Python + Flask 3.0.0 | 5 | 5 | 6 | 5 | **21** | [audit-project-3.md](reports/audit-project-3.md) |

Critérios de aceite: Fase 1 detectou a stack nos 3/3 · ≥ 5 findings nos 3/3 · ≥ 1 CRITICAL/HIGH nos 3/3 · aplicação funcionando após a refatoração nos 3/3 (detalhes abaixo).

### Antes × depois

#### Projeto 1 — code-smells-project

```
ANTES                                   DEPOIS
code-smells-project/                    code-smells-project/
├── app.py        (rotas + admin SQL)   ├── app.py                    entry point fino (python app.py)
├── controllers.py (292 linhas)         ├── .env.example
├── models.py      (314 linhas)         └── src/
├── database.py    (conexão global)         ├── app.py                composition root: create_app()
└── requirements.txt                        ├── config/settings.py    config via env
                                            ├── constants.py · errors.py
                                            ├── database/             connection (flask.g) · schema (FKs) · seed (hash)
                                            ├── models/               produto · usuario · pedido · sistema (SQL parametrizado)
                                            ├── controllers/          produto · usuario · pedido · relatorio · sistema
                                            ├── services/             notification_service
                                            ├── views/                *_routes.py (Blueprints) + validators
                                            └── middlewares/          error_handler · auth (X-Admin-Token)
```

#### Projeto 2 — ecommerce-api-legacy

```
ANTES                                   DEPOIS
src/                                    src/
├── app.js                              ├── app.js                    composition root (createApp + listen)
├── AppManager.js (God Class)           ├── config/index.js           process.env (+ .env opcional)
└── utils.js (config + cache + hash)    ├── constants/ · errors/AppError.js
                                        ├── database/connection.js    wrapper Promise, transaction(), schema c/ FKs, seed
                                        ├── models/                   user · course · enrollment · payment · auditLog
                                        ├── services/paymentService.js
                                        ├── controllers/              checkout · report · user
                                        ├── validators/               checkout · common
                                        ├── routes/                   checkoutRoutes · adminRoutes · userRoutes
                                        ├── middlewares/              asyncHandler · errorHandler · auth
                                        └── utils/                    logger · password (scrypt)
```

#### Projeto 3 — task-manager-api

Projeto já tinha pastas de camadas — a skill **evoluiu** a estrutura existente em vez de recriá-la:

```
ANTES                                   DEPOIS
task-manager-api/                       task-manager-api/
├── app.py   (config hardcoded,         ├── app.py                    composition root: create_app() (python app.py)
│             create_all no import)     ├── .env.example
├── database.py                         ├── config/settings.py        NOVO — config via env
├── seed.py                             ├── database.py               instância SQLAlchemy
├── models/   (MD5, password no         ├── models/                   entidades ORM + acesso a dados (sem password no to_dict)
│              to_dict)                 ├── controllers/              NOVO — task · user · category · report (regras de negócio)
├── routes/   (regra de negócio,        ├── routes/                   só HTTP: main · task · user · category · report + serializers
│              N+1, validação inline)   ├── validators/               NOVO — common · task · user · category
├── services/ (SMTP hardcoded,          ├── middlewares/              NOVO — error_handler · auth (token assinado)
│              não usado)               ├── services/                 notification_service com config injetada
└── utils/    (helpers mortos)          ├── utils/                    constants · errors · helpers puros
                                        └── seed.py                   usa create_app() e grava hashes seguros
```

### Checklist de validação

Legenda: ✅ atendido. Cada item foi conferido no código e/ou na execução registrada em `reports/logs/`.

| Item | P1 | P2 | P3 |
|---|---|---|---|
| **Fase 1** — Linguagem detectada corretamente | ✅ Python | ✅ JavaScript/Node | ✅ Python |
| Framework detectado corretamente | ✅ Flask 3.1.1 | ✅ Express 4.22.1 | ✅ Flask 3.0.0 |
| Domínio descrito corretamente | ✅ E-commerce | ✅ LMS com checkout | ✅ Task Manager |
| Nº de arquivos condiz com a realidade | ✅ 4 | ✅ 3 | ✅ 12 |
| **Fase 2** — Relatório segue o template | ✅ | ✅ | ✅ |
| Cada finding com arquivo e linhas exatos | ✅ | ✅ | ✅ |
| Ordenados CRITICAL → LOW | ✅ | ✅ | ✅ |
| Mínimo de 5 findings | ✅ 21 | ✅ 19 | ✅ 21 |
| APIs deprecated incluídas | ✅ `DEBUG` config | ✅ sqlite3 callbacks, `.verbose()` | ✅ `utcnow()`, `Query.get()` |
| Pausa e pede confirmação antes da Fase 3 | ✅ | ✅ | ✅ |
| **Fase 3** — Estrutura segue MVC | ✅ | ✅ | ✅ |
| Config extraída (sem hardcoded) | ✅ `src/config/settings.py` | ✅ `src/config/index.js` | ✅ `config/settings.py` |
| Models abstraem dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ `src/views/` | ✅ `src/routes/` | ✅ `routes/` |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ `controllers/` |
| Error handling centralizado | ✅ `middlewares/error_handler.py` | ✅ `middlewares/errorHandler.js` | ✅ `middlewares/error_handler.py` |
| Entry point claro | ✅ `app.py` → `create_app()` | ✅ `src/app.js` (`npm start`) | ✅ `app.py` → `create_app()` |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem | ✅ 19/19 | ✅ 3/3 | ✅ 22/22 |

### Evidências (logs das aplicações rodando após a refatoração)

Além da validação feita pela própria skill (registrada nos logs da Fase 3), cada projeto foi revalidado de forma independente, com banco recriado do zero.

**Projeto 1** — `python app.py` + smoke test dos 19 endpoints:

```
GET /                                 200
GET /health                           200
GET /produtos                         200
GET /produtos/busca?q=mouse           200
GET /produtos/1                       200
POST /produtos                        201
PUT /produtos/11                      200
DELETE /produtos/11                   200
GET /usuarios                         200
GET /usuarios/1                       200
POST /usuarios                        201
POST /login (seed admin123)           200
POST /pedidos                         201
GET /pedidos                          200
GET /pedidos/usuario/2                200
PUT /pedidos/1/status                 200
GET /relatorios/vendas                200
POST /admin/query (sem token)         403   ← protegido (antes executava SQL anônimo)
POST /admin/reset-db (com token)      200
"senha" em GET /usuarios? 0 ocorrências
Tracebacks no log do servidor: 0
```

**Projeto 2** — `npm start` + requisições do `api.http`:

```
1 checkout ok:   {"msg":"Sucesso","enrollment_id":2} [200]
2 checkout neg:  Pagamento recusado [400]
3 report sem tk: Não autorizado [401]          ← protegido (antes aberto)
4 report c/ tk:  [{"course":"Clean Architecture","revenue":997,"students":[{"student":"Leonan","paid":997}]},{"course":"Docker","revenue":497,"students":[{"student":"Guilherme","paid":497}]}] [200]
5 delete c/ tk:  Usuário deletado [200]
6 curso inexist: Curso não encontrado [404]
--- server log:
[INFO] LMS API rodando na porta 3000
[INFO] Processando pagamento de 497 com cartão **** 4444   ← cartão mascarado, chave não aparece
[INFO] Checkout concluído: matrícula 2 no curso "Docker"
```

**Projeto 3** — `python seed.py && python app.py` (validado com `PORT=5055`, ver nota abaixo) + smoke test dos 22 endpoints:

```
GET /health                             200
GET /                                   200
GET /tasks                              200
GET /tasks/1                            200
POST /tasks                             201
PUT /tasks/11                           200
GET /tasks/search?q=teste               200
GET /tasks/stats                        200
DELETE /tasks/11                        200
GET /users                              200
GET /users/1                            200
POST /users                             201
PUT /users/4                            200
GET /users/1/tasks                      200
POST /login (seed)                      200
DELETE /users/4 (sem token)             401   ← protegido (antes qualquer um apagava)
DELETE /users/4 (token admin)           200
GET /reports/summary                    200
GET /reports/user/1                     200
GET /categories                         200
POST /categories                        201
PUT /categories/5                       200
DELETE /categories/5                    200
"password" em GET /users/1? 0 ocorrências
Warnings (deprecated) / tracebacks no log do servidor: 0
```

> Nota: durante a validação do projeto 3 a porta 5000 estava ocupada por um servidor de teste do projeto 1 que ficou órfão no ambiente. Como a porta agora vem de configuração, a validação usou `PORT=5055` sem alterar código; a porta padrão continua 5000.

### Mudanças intencionais de contrato (segurança)

| Projeto | Mudança |
|---|---|
| 1 | `senha` removida de `/usuarios`; `secret_key`/`db_path`/`debug` removidos do `/health`; `/admin/*` exigem `X-Admin-Token` (e `/admin/query` também `ENABLE_ADMIN_QUERY=true`); login com SQL injection agora retorna 401; entradas inválidas retornam 400 em vez de 500; respostas de erro ganharam `"sucesso": false`. |
| 2 | `GET /api/admin/financial-report` e `DELETE /api/users/:id` exigem `X-Admin-Token`; DELETE de id inexistente → 404; usuário novo sem `pwd` → 400 (antes criava com senha `123456`); payload malformado → 400 em vez de derrubar o processo. |
| 3 | `password` (hash) removido de todas as respostas de usuário; `token` do `/login` passou a ser assinado (itsdangerous + `SECRET_KEY`) no lugar de `fake-jwt-token-<id>`; `DELETE /users/<id>` e atribuição/alteração de role privilegiada exigem `Authorization: Bearer <token de admin>` (401/403); CORS padrão restrito a `localhost:3000` (`CORS_ORIGINS=*` restaura); entradas inválidas → 400 JSON em vez de 500; `tasks.db` antigo (MD5) precisa ser recriado com `python seed.py`. |

### Observações sobre o comportamento em stacks diferentes

- **Monolito Python (P1):** a skill identificou corretamente o caso de "pseudo-camadas" (arquivos chamados `models.py`/`controllers.py` com responsabilidades misturadas) e criou um pacote `src/` completo, mantendo `python app.py` como comando de execução através de um entry point fino. Também tratou migração de senhas legadas em texto puro num `loja.db` já existente.
- **Node/Express (P2):** o ponto central foi o *callback hell* — a skill promisificou o driver `sqlite3`, introduziu `asyncHandler` (Express 4 não captura rejeições de handlers `async`) e transações explícitas. Preservou os nomes externos abreviados do contrato (`usr`, `eml`, `pwd`, `c_id`, `card`) mapeando-os para nomes claros na borda.
- **Flask com camadas parciais (P3):** a skill classificou o projeto como "camadas parciais — rotas gordas" e, em vez de reescrevê-lo, manteve `models/`, `routes/`, `services/` e `utils/`, criando apenas o que faltava (`controllers/`, `validators/`, `middlewares/`, `config/`). Encontrou problemas mesmo com a organização existente (MD5, hash exposto, token falso, N+1, APIs deprecated `utcnow`/`Query.get`) e manteve `python seed.py` funcionando com a nova factory.
- Nos três casos a skill pausou corretamente após a Fase 2 sem tocar em arquivos, e em nenhum caso alterou porta ou comando de execução.

---

## D) Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado (`claude --version`; usado: 2.1.318)
- Python 3.10+ (testado em 3.14) e Node.js 20.12+ (testado em 24)

### Executar a skill em cada projeto

A skill fica em `.claude/skills/refactor-arch/` dentro de cada projeto, então basta abrir o Claude Code na pasta do projeto:

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch ../reports/audit-project-1.md"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch ../reports/audit-project-2.md"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch ../reports/audit-project-3.md"
```

O argumento (caminho do relatório) é opcional; sem ele o relatório vai para `<raiz-do-repo>/reports/audit-<nome-do-projeto>.md`. A skill imprime a Fase 1, a Fase 2 e **para** em `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` — responda `y` para refatorar.

Modo não interativo (como foi executado para esta entrega):

```bash
cd code-smells-project
claude -p "/refactor-arch ../reports/audit-project-1.md" --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep" > ../reports/logs/project-1-phase-1-2.log
claude -p --continue "y" --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep" > ../reports/logs/project-1-phase-3.log
```

### Como validar que a refatoração funcionou

**Projeto 1 — code-smells-project** (porta 5000)
```bash
cd code-smells-project
pip install -r requirements.txt
ADMIN_TOKEN=dev-token python app.py
curl localhost:5000/produtos
curl -X POST localhost:5000/login -H "Content-Type: application/json" -d '{"email":"admin@loja.com","senha":"admin123"}'
curl -X POST localhost:5000/admin/reset-db -H "X-Admin-Token: dev-token"
```

**Projeto 2 — ecommerce-api-legacy** (porta 3000)
```bash
cd ecommerce-api-legacy
npm install
ADMIN_TOKEN=dev-token npm start
# use as requisições de api.http (rotas admin com header X-Admin-Token: dev-token)
```

**Projeto 3 — task-manager-api** (porta 5000)
```bash
cd task-manager-api
pip install -r requirements.txt
python seed.py        # obrigatório antes do primeiro boot (grava senhas com hash)
python app.py
curl localhost:5000/tasks
TOKEN=$(curl -s -X POST localhost:5000/login -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","password":"1234"}' | python -c "import sys,json;print(json.load(sys.stdin)['token'])")
curl -X DELETE localhost:5000/users/3 -H "Authorization: Bearer $TOKEN"
```

Variáveis de ambiente de cada projeto estão documentadas no respectivo `.env.example`. As portas padrão (5000/3000) foram mantidas; para rodar os dois projetos Flask ao mesmo tempo use `PORT=5001`.
