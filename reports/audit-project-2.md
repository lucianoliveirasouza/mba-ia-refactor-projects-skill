================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js 24) + Express 4.22.1
Files:   3 analyzed | ~180 lines of code
Date:    2026-11-04

## Summary
CRITICAL: 5 | HIGH: 5 | MEDIUM: 5 | LOW: 4

| ID | Severity | Anti-pattern | Location |
|----|----------|--------------|----------|
| F-01 | CRITICAL | God Class | src/AppManager.js:4-139 |
| F-02 | CRITICAL | Armazenamento inseguro de senha | src/AppManager.js:18, src/AppManager.js:68, src/utils.js:17-23 |
| F-03 | CRITICAL | Exposição de dados sensíveis em log | src/AppManager.js:45 |
| F-04 | CRITICAL | Endpoints perigosos sem proteção | src/AppManager.js:80, src/AppManager.js:131 |
| F-05 | CRITICAL | Credenciais hardcoded | src/utils.js:1-7 |
| F-06 | HIGH | Acoplamento forte sem DI | src/AppManager.js:7, src/app.js:8-10 |
| F-07 | HIGH | Escrita múltipla sem transação / integridade quebrada | src/AppManager.js:12-16, src/AppManager.js:50-61, src/AppManager.js:133-135 |
| F-08 | HIGH | Fat Controller | src/AppManager.js:28-78, src/AppManager.js:80-129 |
| F-09 | HIGH | Callback Hell / erros ignorados | src/AppManager.js:37-77, src/AppManager.js:83-128 |
| F-10 | HIGH | Estado global mutável | src/utils.js:9-15 |
| F-11 | MEDIUM | Validação de entrada ausente | src/AppManager.js:29-35, src/AppManager.js:46, src/AppManager.js:68, src/AppManager.js:132 |
| F-12 | MEDIUM | Error handling não centralizado | src/AppManager.js:35-84, src/AppManager.js:133-135, src/app.js:5-10 |
| F-13 | MEDIUM | API deprecated (sqlite3 callbacks) | src/AppManager.js:1, src/AppManager.js:37-133 |
| F-14 | MEDIUM | Queries N+1 | src/AppManager.js:89-106 |
| F-15 | MEDIUM | Duplicação de código | src/AppManager.js:95-99, src/AppManager.js:117-122 |
| F-16 | LOW | Imports não usados / código morto | src/AppManager.js:2, src/utils.js:2-5, src/utils.js:9-10, src/utils.js:25 |
| F-17 | LOW | Nomenclatura ruim | src/AppManager.js:4, src/AppManager.js:26, src/AppManager.js:29-33, src/utils.js:17 |
| F-18 | LOW | Magic numbers e strings | src/AppManager.js:46, src/AppManager.js:68, src/AppManager.js:108, src/utils.js:19-22 |
| F-19 | LOW | console.log como logging | src/app.js:13, src/utils.js:13 |

## Findings

### F-01 [CRITICAL] God Class (AP-03)
File: src/AppManager.js:4-139
Description: A classe `AppManager` acumula: criação da conexão (`new sqlite3.Database(':memory:')`, l.7), criação de schema e seed (`initDb`, l.10-23), registro de todas as rotas HTTP (`setupRoutes`, l.25-138), SQL, validação de entrada, processamento de pagamento (l.46) e montagem do relatório financeiro. `setupRoutes` sozinho tem ~113 linhas.
Impact: Nada é testável isoladamente; qualquer mudança em pagamento, relatório ou usuário toca o mesmo arquivo; viola SRP por completo.
Recommendation: Quebrar em config, `database` (conexão + schema/seed), models por domínio (`userModel`, `courseModel`, `enrollmentModel`, `paymentModel`, `auditLogModel`), controllers/services (`checkout`, `report`, `user`), routes e composition root (PB-03 + PB-04).

### F-02 [CRITICAL] Armazenamento inseguro de senha (AP-06)
File: src/AppManager.js:18, src/AppManager.js:68, src/utils.js:17-23
Description: O seed grava senha em texto puro (`pass = '123'`, l.18). Usuários novos usam `badCrypto` — base64 da senha repetido 10000 vezes e truncado em 10 caracteres, sem salt, determinístico (só depende dos 2 primeiros chars do base64). Se `pwd` não é enviado, assume senha padrão `"123456"` (l.68).
Impact: Vazamento do banco expõe todas as senhas trivialmente; senhas distintas colidem no mesmo "hash"; contas criadas no checkout ficam com senha previsível.
Recommendation: `crypto.scrypt` com salt aleatório (módulo nativo, sem nova dependência) em `src/utils/password.js`; hashear a senha do seed; não criar contas com senha padrão (PB-08).

### F-03 [CRITICAL] Exposição de dados sensíveis em log (AP-05)
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` grava o número completo do cartão e a chave live do gateway no stdout a cada checkout.
Impact: Vazamento de PAN (violação PCI-DSS) e da chave de pagamento de produção para qualquer agregador de logs.
Recommendation: Logger central sem dados sensíveis; registrar apenas cartão mascarado (últimos 4 dígitos) e nunca a chave (PB-15).

### F-04 [CRITICAL] Endpoints perigosos sem proteção (AP-04)
File: src/AppManager.js:80, src/AppManager.js:131
Description: `GET /api/admin/financial-report` (receita e nomes de alunos) e `DELETE /api/users/:id` não possuem nenhuma autenticação/autorização.
Impact: Qualquer anônimo lê dados financeiros e apaga usuários.
Recommendation: Middleware `requireAdmin` validando token (`ADMIN_TOKEN` em env) via header, respondendo 401/403; manter as rotas (PB-09).

### F-05 [CRITICAL] Credenciais hardcoded (AP-01)
File: src/utils.js:1-7
Description: Objeto `config` literal com `dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, `smtpUser` e `port: 3000` fixos.
Impact: Credenciais de produção expostas a quem acessa o repositório; rotação exige deploy.
Recommendation: `src/config/index.js` lendo `process.env` com defaults seguros apenas para dev + `.env.example` (PB-01).

### F-06 [HIGH] Acoplamento forte sem injeção de dependência (AP-09)
File: src/AppManager.js:7, src/app.js:8-10
Description: O construtor instancia o driver diretamente (`new sqlite3.Database(':memory:')`); rotas usam `this.db` cru; não há composition root — `app.js` apenas chama `initDb()`/`setupRoutes(app)`.
Impact: Impossível trocar o banco ou injetar mocks em testes; rotas conhecem o driver.
Recommendation: Criar a conexão no composition root (`app.js`) e injetá-la em models → controllers (PB-06).

### F-07 [HIGH] Escrita múltipla sem transação / integridade quebrada (AP-11)
File: src/AppManager.js:12-16, src/AppManager.js:50-61, src/AppManager.js:133-135
Description: Checkout faz INSERT em `users` → `enrollments` → `payments` → `audit_logs` sem `BEGIN/COMMIT`; falha no pagamento deixa matrícula sem pagamento. Tabelas sem FOREIGN KEY. `DELETE` de usuário deixa matrículas/pagamentos órfãos — a própria resposta admite: "as matrículas e pagamentos ficaram sujos no banco".
Impact: Dados inconsistentes (matrículas sem pagamento, relatórios com alunos "Unknown").
Recommendation: Transação no service de checkout (`BEGIN/COMMIT/ROLLBACK`), FKs com `ON DELETE CASCADE` + `PRAGMA foreign_keys = ON`, remoção do usuário e dependentes em transação (PB-11).

### F-08 [HIGH] Fat Controller (AP-07)
File: src/AppManager.js:28-78, src/AppManager.js:80-129
Description: Handler de checkout (50 linhas) busca curso, localiza/cria usuário, decide aprovação do pagamento (`cc.startsWith("4")`), cria matrícula, pagamento, audit log e cache. Handler do relatório (50 linhas) agrega receita e alunos manualmente.
Impact: Regra de pagamento e de faturamento acoplada ao HTTP; não reutilizável nem testável.
Recommendation: `checkoutService`/`reportService` com a regra de negócio; controllers finos que só traduzem request→service→response (PB-04).

### F-09 [HIGH] Callback Hell / async sem propagação de erro (AP-10)
File: src/AppManager.js:37-77, src/AppManager.js:83-128
Description: Até 6 níveis de callbacks aninhados, contadores manuais (`coursesPending--`, `enrPending--`), mistura de `function(err){ this.lastID }` com `self`. Erros ignorados: l.57 (audit log), l.92-93 (`enrollments.length` com `err` → TypeError derruba o processo), l.104, l.106, l.133.
Impact: Exceções em callbacks do sqlite3 não são capturadas pelo Express e derrubam o servidor; requisições podem ficar sem resposta em erro parcial.
Recommendation: Promisificar o acesso ao banco (`run/get/all` → Promises), `async/await` com `try/catch` encaminhando ao error handler (PB-10).

### F-10 [HIGH] Estado global mutável (AP-08)
File: src/utils.js:9-15
Description: `let globalCache = {}` mutado por `logAndCache` a cada checkout (`last_checkout_${userId}`) e `let totalRevenue = 0` exportado como valor de módulo.
Impact: Vazamento de memória (cache cresce sem limite e nunca é lido), estado compartilhado entre requisições/testes.
Recommendation: Remover o cache write-only e `totalRevenue` (não são lidos em lugar nenhum); se cache for necessário, injetá-lo como dependência (PB-06).

### F-11 [MEDIUM] Validação de entrada ausente (AP-14)
File: src/AppManager.js:29-35, src/AppManager.js:46, src/AppManager.js:68, src/AppManager.js:132
Description: Só checa truthiness de `usr`, `eml`, `c_id`, `card`; não verifica tipo (`card` numérico → `cc.startsWith` lança TypeError dentro do callback e derruba o processo), nem formato de e-mail; `pwd` é opcional com fallback `"123456"`; `:id` do DELETE não é validado; `req.body` pode ser `undefined` sem JSON.
Impact: Payload malformado derruba o servidor (DoS trivial); contas criadas com dados inválidos.
Recommendation: Validador do checkout na camada de rotas (strings não vazias, `c_id` inteiro positivo, `card` string numérica) e validação de `id` inteiro, respondendo 400 (PB-12).

### F-12 [MEDIUM] Error handling não centralizado (AP-15)
File: src/AppManager.js:35, src/AppManager.js:38, src/AppManager.js:41, src/AppManager.js:48, src/AppManager.js:51, src/AppManager.js:55, src/AppManager.js:70, src/AppManager.js:84, src/AppManager.js:133-135, src/app.js:5-10
Description: Cada callback responde erro de um jeito, em texto puro (`"Erro DB"`, `"Erro Matrícula"`…); erro de banco no curso vira 404 (l.38); DELETE responde 200 mesmo com erro ou id inexistente; não há middleware de erro do Express.
Impact: Respostas inconsistentes, falhas mascaradas, nenhum ponto único de log.
Recommendation: Classes de erro (`NotFoundError`, `ValidationError`…) + middleware de erro central em `src/middlewares/errorHandler.js`, preservando mensagens/status atuais do contrato (PB-05).

### F-13 [MEDIUM] Uso de API deprecated/legada (AP-17)
File: src/AppManager.js:1, src/AppManager.js:37-133
Description: Uso da API de callbacks do `sqlite3` sem promisificação (todas as chamadas `db.run/get/all`) e `require('sqlite3').verbose()` (modo debug com stack traces longos) em código de aplicação.
Impact: Impede `async/await`, gera F-09 e overhead de debug em produção.
Recommendation: Wrapper de Promises sobre `sqlite3` (`src/database/connection.js`) e remoção do `.verbose()` fora de dev (PB-13).

### F-14 [MEDIUM] Queries N+1 (AP-13)
File: src/AppManager.js:89-106
Description: Para cada curso, uma query em `enrollments` (l.92); para cada matrícula, uma query em `users` (l.104) e outra em `payments` (l.106) — 1 + C + 2E queries.
Impact: Relatório degrada linearmente com o número de matrículas.
Recommendation: Uma única query com `LEFT JOIN` courses→enrollments→users→payments agregada em memória no service (PB-07).

### F-15 [MEDIUM] Duplicação de código (AP-16)
File: src/AppManager.js:95-99, src/AppManager.js:117-122
Description: O bloco "push no report, decrementa `coursesPending`, se 0 `res.json(report)`" está duplicado nos dois ramos.
Impact: Fácil esquecer um dos ramos (resposta dupla ou nunca enviada).
Recommendation: Eliminado naturalmente pela query única + agregação (PB-16/PB-07).

### F-16 [LOW] Imports não usados e código morto (AP-21)
File: src/AppManager.js:2, src/utils.js:2-5, src/utils.js:9-10, src/utils.js:25
Description: `totalRevenue` importado e nunca usado (AppManager.js:2); `dbUser`, `dbPass`, `smtpUser` sem nenhum uso; `globalCache` exportado e nunca lido.
Impact: Ruído e falsa impressão de funcionalidade.
Recommendation: Remover (PB-16).

### F-17 [LOW] Nomenclatura ruim (AP-19)
File: src/AppManager.js:4, src/AppManager.js:26, src/AppManager.js:29-33, src/utils.js:17
Description: Variáveis `u`, `e`, `p`, `cid`, `cc`; `const self = this`; classe genérica `AppManager`; função `badCrypto`; `utils.js` contendo config.
Impact: Leitura difícil; nomes não revelam intenção.
Recommendation: Renomear internamente (`name`, `email`, `password`, `courseId`, `cardNumber`) preservando os campos externos `usr/eml/pwd/c_id/card` do contrato (PB-14).

### F-18 [LOW] Magic numbers e strings (AP-18)
File: src/AppManager.js:46, src/AppManager.js:68, src/AppManager.js:108, src/utils.js:19-22
Description: Regra de aprovação `cc.startsWith("4")`; status `"PAID"`/`"DENIED"` literais; senha padrão `"123456"`; `10000` iterações e truncamento `10` no hash.
Impact: Regra de negócio escondida e espalhada.
Recommendation: Constantes nomeadas (`PAYMENT_STATUS`, `APPROVED_CARD_PREFIX`) em `src/constants` (PB-14).

### F-19 [LOW] console.log como logging (AP-20)
File: src/app.js:13, src/utils.js:13
Description: `console.log` para boot e "[LOG] Salvando no cache" (o log com cartão já está em F-03).
Impact: Sem níveis, sem possibilidade de silenciar/redirecionar.
Recommendation: Logger simples centralizado com níveis (PB-15).

## Deprecated APIs
| Location | Deprecated | Modern replacement |
|----------|-----------|--------------------|
| src/AppManager.js:37-133 | sqlite3 API de callbacks sem promisificação | wrapper com Promises + async/await |
| src/AppManager.js:1 | `sqlite3.verbose()` em código de produção | `require('sqlite3')` (verbose só em dev) |

Nenhuma API Express 4→5 deprecated detectada (já usa `res.status().send()`, `express.json()`).

## Architecture Snapshot
Current:  Monolítica — God Class (AppManager) com schema, seed, SQL, regra de pagamento e rotas
Target:   MVC — config / models / views(routes) / controllers / middlewares / composition root

================================
Total: 19 findings
================================
