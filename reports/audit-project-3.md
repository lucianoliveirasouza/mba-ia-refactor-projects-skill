================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   12 analyzed | ~1155 lines of code
Date:    2026-11-04

## Summary
CRITICAL: 5 | HIGH: 5 | MEDIUM: 6 | LOW: 5

| ID | Severity | Anti-pattern | Location |
|----|----------|--------------|----------|
| F-01 | CRITICAL | Credenciais e segredos hardcoded | app.py:13 |
| F-02 | CRITICAL | Configuração insegura de runtime (debug + 0.0.0.0) | app.py:34 |
| F-03 | CRITICAL | Exposição de dados sensíveis (hash de senha nas respostas) | models/user.py:16-25 |
| F-04 | CRITICAL | Armazenamento inseguro de senha (MD5) | models/user.py:29 |
| F-05 | CRITICAL | Endpoints perigosos sem proteção / escalonamento de privilégio | routes/user_routes.py:52 |
| F-06 | HIGH | Acoplamento forte sem injeção de dependência / sem composition root | app.py:9-31 |
| F-07 | HIGH | CORS aberto para qualquer origem | app.py:15 |
| F-08 | HIGH | Integridade referencial quebrada | models/task.py:20-21 |
| F-09 | HIGH | Fat Controller (regra de negócio nas rotas) | routes/report_routes.py:12-101 |
| F-10 | HIGH | Token de autenticação falso/previsível | routes/user_routes.py:210 |
| F-11 | MEDIUM | API deprecated: datetime.utcnow() | models/category.py:11 |
| F-12 | MEDIUM | Queries N+1 | routes/report_routes.py:15-28 |
| F-13 | MEDIUM | Duplicação de código | routes/report_routes.py:34-37 |
| F-14 | MEDIUM | API deprecated: Model.query.get() | routes/report_routes.py:105 |
| F-15 | MEDIUM | Error handling não centralizado / except nu | routes/report_routes.py:186 |
| F-16 | MEDIUM | Validação ausente, inconsistente ou duplicada | routes/report_routes.py:196 |
| F-17 | LOW | Imports não usados e código morto | app.py:7 |
| F-18 | LOW | Condicionais verbosas | models/task.py:38-60 |
| F-19 | LOW | Nomenclatura ruim | routes/report_routes.py:10 |
| F-20 | LOW | Magic numbers e strings | routes/report_routes.py:45 |
| F-21 | LOW | print como logging | routes/task_routes.py:149 |

## Findings

### F-01 [CRITICAL] Credenciais e segredos hardcoded (AP-01)
File: app.py:11, app.py:13, services/notification_service.py:7-10
Description: `SECRET_KEY = 'super-secret-key-123'` fixo no código, e o `NotificationService` traz `email_user = 'taskmanager@gmail.com'` e `email_password = 'senha123'` como literais. A URI do banco (`sqlite:///tasks.db`) também está fixa.
Impact: qualquer pessoa com acesso ao repositório pode forjar sessões assinadas e usar a conta SMTP. Trocar a chave exige um novo deploy.
Recommendation: criar um módulo `config` que lê variáveis de ambiente (python-dotenv já está no requirements) com defaults seguros só para desenvolvimento, além de um `.env.example` (PB-01).

### F-02 [CRITICAL] Configuração insegura de runtime (AP-12)
File: app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)`. O debugger do Werkzeug fica exposto em todas as interfaces de rede. A severidade subiu de HIGH para CRITICAL por causa da combinação debug + 0.0.0.0.
Impact: execução remota de código pelo console interativo do debugger.
Recommendation: definir debug, host e porta por variáveis de ambiente (`FLASK_DEBUG`, `HOST`, `PORT`), com debug desligado por padrão (PB-01).

### F-03 [CRITICAL] Exposição de dados sensíveis (AP-05)
File: models/user.py:16-25, routes/user_routes.py:33, routes/user_routes.py:85, routes/user_routes.py:129, routes/user_routes.py:209
Description: `User.to_dict()` inclui `'password': self.password`. Esse dict é devolvido em GET /users/<id>, POST /users, PUT /users/<id> e dentro de `user` no POST /login.
Impact: o hash da senha (MD5, ver F-04) vaza para qualquer cliente e é quebrado de forma trivial.
Recommendation: serializar por whitelist, sem o campo `password` (PB-09). Essa é uma mudança de contrato aceita por ser correção de segurança.

### F-04 [CRITICAL] Armazenamento inseguro de senha (AP-06)
File: models/user.py:29, models/user.py:32
Description: `hashlib.md5(pwd.encode()).hexdigest()`, sem salt, usado no cadastro e no login. O padrão seria HIGH. Subiu para CRITICAL porque está no caminho de autenticação e porque o hash é exposto (F-03).
Impact: com rainbow tables, as senhas ficam recuperáveis na hora.
Recommendation: usar `werkzeug.security.generate_password_hash`/`check_password_hash` no model User (PB-08). O seed passa a gerar hashes novos, e o login com as credenciais de seed continua funcionando.

### F-05 [CRITICAL] Endpoints perigosos sem proteção (AP-04)
File: routes/user_routes.py:52, routes/user_routes.py:71, routes/user_routes.py:119-122, routes/user_routes.py:134-151
Description: não há nenhuma autenticação ou autorização na API. Qualquer cliente anônimo pode criar um usuário com `role='admin'` (POST /users aceita `role` do body), promover qualquer usuário a admin (PUT /users/<id> com `role`) e apagar usuários junto com todas as suas tasks (DELETE /users/<id>).
Impact: escalonamento de privilégio e destruição de dados sem credencial.
Recommendation: criar um middleware de auth com token assinado (ver F-10) e um decorator `require_admin` para atribuição de role privilegiada e para exclusão de usuários, preservando as rotas e respondendo 401/403 (PB-09).

### F-06 [HIGH] Acoplamento forte sem injeção de dependência (AP-09)
File: app.py:9-31, routes/task_routes.py:2-5, routes/user_routes.py:2-4, routes/report_routes.py:2-5, services/notification_service.py:5-10, services/notification_service.py:15, seed.py:2
Description: a app é criada no import do módulo, com `db.create_all()` como efeito colateral (app.py:30-31). Não existe `create_app()`. As rotas importam `db` e os models e fazem as queries direto. O `NotificationService` monta a própria config e instancia `smtplib.SMTP` internamente. O `seed.py` depende de importar `app`.
Impact: não dá para testar em isolamento nem trocar o banco ou a config. Importar qualquer módulo já toca o banco.
Recommendation: criar uma app factory como composition root, uma camada de controllers/repositórios por domínio e um service de notificação que recebe a config por injeção (PB-06, PB-03).

### F-07 [HIGH] CORS aberto (AP-12)
File: app.py:15
Description: `CORS(app)`, sem lista de origens, libera `*` em todas as rotas, inclusive /login e /users.
Impact: qualquer site pode chamar a API a partir do navegador da vítima.
Recommendation: definir as origens permitidas por `CORS_ORIGINS` no config (PB-01).

### F-08 [HIGH] Integridade referencial quebrada (AP-11)
File: models/task.py:20-21, routes/report_routes.py:211-223, routes/user_routes.py:140-142
Description: os relacionamentos `db.relationship('User', backref='tasks')` e `('Category', backref='tasks')` não definem cascade nem `ondelete`. DELETE /categories/<id> apaga a categoria e deixa as tasks com um `category_id` que não existe mais (o SQLite não aplica FK por padrão). A exclusão de usuário trata a cascata à mão, num loop dentro da rota.
Impact: tasks órfãs com `category_id` inválido, e `category_name` inconsistente nos relatórios.
Recommendation: tratar a remoção de forma explícita e transacional no controller (desvincular `category_id` das tasks da categoria; cascata de tasks em User pelo ORM) (PB-11).

### F-09 [HIGH] Fat Controller, regra de negócio nas rotas (AP-07)
File: routes/report_routes.py:12-101, routes/report_routes.py:103-155, routes/task_routes.py:11-63, routes/task_routes.py:85-154, routes/task_routes.py:156-223, routes/task_routes.py:273-299, routes/user_routes.py:42-90
Description: os handlers HTTP fazem tudo: validação, cálculo de atraso, estatísticas por status/prioridade/usuário, taxa de conclusão e montagem manual de JSON. `summary_report` tem cerca de 90 linhas e 15 consultas (God Method). `report_routes.py` acumula relatórios e o CRUD de categorias.
Impact: as regras não podem ser reutilizadas nem testadas sem HTTP, e qualquer mudança mexe em vários handlers.
Recommendation: mover as regras para controllers/services por domínio (tasks, users, categories, reports) e deixar as rotas só com o mapeamento HTTP (PB-04).

### F-10 [HIGH] Token falso/previsível (AP-05)
File: routes/user_routes.py:210
Description: o login devolve `'token': 'fake-jwt-token-' + str(user.id)`, que é previsível e não é assinado.
Impact: qualquer cliente pode "forjar" o token de outro usuário. Não serve como base para auth.
Recommendation: gerar um token assinado com `SECRET_KEY` (itsdangerous, já incluído no Flask), mantendo o campo `token` na resposta, e validá-lo no middleware de auth (PB-09).

### F-11 [MEDIUM] API deprecated: datetime.utcnow() (AP-17)
File: models/category.py:11, models/task.py:15-16, models/task.py:52, models/user.py:14, routes/report_routes.py:35, routes/report_routes.py:42, routes/report_routes.py:45, routes/report_routes.py:71, routes/report_routes.py:133, routes/task_routes.py:31, routes/task_routes.py:72, routes/task_routes.py:215, routes/task_routes.py:285, routes/user_routes.py:172, services/notification_service.py:35, utils/helpers.py:38, seed.py:66-74
Description: `datetime.utcnow()` está deprecated desde o Python 3.12 (o runtime local é o 3.14.8) e gera DeprecationWarning.
Impact: avisos hoje e remoção numa versão futura.
Recommendation: usar uma função utilitária `utcnow()` que retorna `datetime.now(timezone.utc).replace(tzinfo=None)`, preservando os datetimes naive do banco (PB-13).

### F-12 [MEDIUM] Queries N+1 (AP-13)
File: routes/report_routes.py:15-28, routes/report_routes.py:55-56, routes/report_routes.py:163, routes/task_routes.py:41-57, routes/task_routes.py:275-279, routes/user_routes.py:22
Description: GET /tasks faz `User.query.get` e `Category.query.get` para cada task. `summary_report` roda 12 `count()` separados e mais uma query por usuário. GET /categories faz um `count()` por categoria. GET /users acessa a relação lazy `len(u.tasks)` dentro do loop. As contagens por status em /tasks/stats também são feitas uma a uma.
Impact: o número de queries cresce linearmente com os dados.
Recommendation: usar `GROUP BY` com `func.count` e eager loading (`joinedload`/`selectinload`) nos models/repositórios (PB-07).

### F-13 [MEDIUM] Duplicação de código (AP-16)
File: routes/report_routes.py:34-37, routes/report_routes.py:132-135, routes/report_routes.py:67, routes/report_routes.py:151, routes/task_routes.py:17-28, routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/task_routes.py:140-144, routes/task_routes.py:209-213, routes/task_routes.py:283-287, routes/task_routes.py:296, routes/user_routes.py:61, routes/user_routes.py:106, routes/user_routes.py:162-180
Description: a regra de "task atrasada" é reimplementada 6 vezes, embora `Task.is_overdue()` exista (models/task.py:50). A serialização campo a campo da task repete `Task.to_dict()`. A taxa de conclusão aparece 3 vezes, ignorando `calculate_percentage`. A regex de email aparece 2 vezes, ignorando `validate_email`. A conversão de tags aparece 2 vezes.
Impact: as regras divergem com o tempo, e uma correção precisa ser feita em N lugares.
Recommendation: centralizar no model (`is_overdue`, `to_dict`), nos validators e nos utils (PB-16).

### F-14 [MEDIUM] API deprecated: Model.query.get() (AP-17)
File: routes/report_routes.py:105, routes/report_routes.py:192, routes/report_routes.py:213, routes/task_routes.py:42, routes/task_routes.py:51, routes/task_routes.py:67, routes/task_routes.py:117, routes/task_routes.py:122, routes/task_routes.py:158, routes/task_routes.py:188, routes/task_routes.py:195, routes/task_routes.py:227, routes/user_routes.py:29, routes/user_routes.py:94, routes/user_routes.py:136, routes/user_routes.py:155
Description: `Query.get()` é legado no SQLAlchemy 2.x (exigido pelo Flask-SQLAlchemy 3.1.1) e emite LegacyAPIWarning.
Impact: avisos hoje e remoção no SQLAlchemy 2.1+/3.
Recommendation: trocar por `db.session.get(Model, id)` (PB-13).

### F-15 [MEDIUM] Error handling não centralizado (AP-15)
File: routes/report_routes.py:186, routes/report_routes.py:207, routes/report_routes.py:221, routes/task_routes.py:62, routes/task_routes.py:137, routes/task_routes.py:204, routes/task_routes.py:236, routes/user_routes.py:130, routes/user_routes.py:149, utils/helpers.py:46, utils/helpers.py:49, utils/helpers.py:88
Description: há 12 `except:` nus e um `try/rollback/500` copiado em cada handler. Não existe `@app.errorhandler`: um 404 de rota inexistente ou um erro não tratado devolve HTML em vez de JSON `{'error': ...}`.
Impact: erros de programação são engolidos sem log, e o formato de erro é inconsistente.
Recommendation: criar um middleware de erros com exceções de domínio (`NotFoundError`, `ValidationError`, `ConflictError`) mapeadas para JSON, com rollback central (PB-05).

### F-16 [MEDIUM] Validação ausente, inconsistente ou duplicada (AP-14)
File: routes/report_routes.py:196-202, routes/task_routes.py:96-114, routes/task_routes.py:166-184, routes/task_routes.py:261, routes/task_routes.py:264, routes/user_routes.py:71, routes/user_routes.py:102-125, utils/helpers.py:57-108
Description: PUT /categories não checa se `get_json()` é `None`, o que dá TypeError e 500. `priority < 1` com valor string (ex.: `"2"`) dá TypeError e 500 em POST/PUT /tasks. `len(data['title'])` com `null` dá 500. `int(priority)` e `int(user_id)` em /tasks/search dão 500 com entrada não numérica. Nome e `active` não são validados no PUT /users, nem a cor da categoria (`is_valid_color` existe e não é usado). As listas de status/roles se repetem em 5 lugares. O helper `process_task_data` existe e não é usado.
Impact: erros 500 provocados pelo cliente e regras divergentes entre create e update.
Recommendation: criar uma camada de validators única por domínio com constantes compartilhadas, retornando 400 (PB-12).

### F-17 [LOW] Imports não usados e código morto (AP-21)
File: app.py:7, models/task.py:3, routes/task_routes.py:7, routes/user_routes.py:6, routes/report_routes.py:7-8, utils/helpers.py:3-7, utils/helpers.py:9-116, services/notification_service.py:1-48, models/task.py:38-48, models/user.py:34-38
Description: imports sem uso: `os, sys, json` (app.py), `json, os, sys, time` (task_routes), `hashlib, json` (user_routes), `format_date, calculate_percentage, json` (report_routes) e `os, json, sys, math, hashlib` (helpers). Nenhuma função ou constante de `utils/helpers.py` é usada de fato. `NotificationService` nunca é instanciado. `validate_status`, `validate_priority` e `is_admin` não são chamados.
Impact: ruído e falsa impressão de que existem validações e notificações.
Recommendation: remover ou passar a usar (validators e constantes reaproveitados na nova camada) (PB-16/PB-12).

### F-18 [LOW] Condicionais verbosas (AP-22)
File: models/task.py:38-60, models/user.py:34-38, utils/helpers.py:21-23, utils/helpers.py:53-55, routes/task_routes.py:141, routes/task_routes.py:210, utils/helpers.py:103
Description: há `if cond: return True else: return False` e `is_overdue` com 3 níveis de `if` aninhados, além de `type(tags) == list`.
Impact: legibilidade.
Recommendation: usar expressões booleanas diretas e `isinstance` (PB-14).

### F-19 [LOW] Nomenclatura ruim (AP-19)
File: routes/report_routes.py:10, routes/report_routes.py:157-223, routes/report_routes.py:24-28, routes/user_routes.py:12-14
Description: `report_bp`/`report_routes.py` também contém o CRUD de `/categories` (o nome não corresponde ao conteúdo). Há variáveis como `p1`..`p5`, `u`, `t`, `c` e `cat` fora de loops curtos.
Impact: é difícil localizar responsabilidades.
Recommendation: criar um módulo de rotas próprio para categorias e usar nomes descritivos, mantendo os caminhos externos (PB-14).

### F-20 [LOW] Magic numbers e strings (AP-18)
File: routes/report_routes.py:45, routes/report_routes.py:129, routes/report_routes.py:180, routes/task_routes.py:96, routes/task_routes.py:99, routes/task_routes.py:104, routes/task_routes.py:113, routes/task_routes.py:167-182, routes/user_routes.py:64, routes/user_routes.py:115
Description: há literais soltos: `3`/`200` (tamanho do título), `1`/`5` (prioridade), `3` (prioridade padrão), `4` (senha mínima), `days=7`, `priority <= 2` (alta prioridade), `'#000000'` e os status literais `'done'`/`'cancelled'`. As constantes já existem em `utils/helpers.py:110-116`, mas não são usadas.
Impact: as regras ficam escondidas e são difíceis de ajustar.
Recommendation: definir as constantes de domínio num único módulo (PB-14).

### F-21 [LOW] print como logging (AP-20)
File: routes/task_routes.py:149, routes/task_routes.py:153, routes/task_routes.py:219, routes/task_routes.py:234, routes/user_routes.py:83, routes/user_routes.py:89, routes/user_routes.py:147, services/notification_service.py:21, services/notification_service.py:24, utils/helpers.py:39, utils/helpers.py:41
Description: eventos e erros vão para o stdout via `print`, incluindo `str(e)` de exceções do banco.
Impact: não há níveis de log nem destino configurável.
Recommendation: usar o módulo `logging` (logger por módulo) (PB-15). O `print` do `seed.py` é saída de CLI e foi mantido fora do finding.

## Deprecated APIs
| Location | Deprecated | Modern replacement |
|----------|-----------|--------------------|
| models/*.py, routes/*.py, services/notification_service.py:35, utils/helpers.py:38, seed.py:66-74 (ver F-11) | `datetime.utcnow()` (Python ≥ 3.12; runtime 3.14.8) | `datetime.now(timezone.utc).replace(tzinfo=None)` |
| routes/*.py, 16 ocorrências (ver F-14) | `Model.query.get(id)` (SQLAlchemy 2.x legacy) | `db.session.get(Model, id)` |
| models/user.py:29, 32 (ver F-04) | `hashlib.md5` para senha | `werkzeug.security.generate_password_hash` |
| routes/task_routes.py:141, 210, utils/helpers.py:103 (ver F-18) | `type(x) == list` | `isinstance(x, list)` |

## Architecture Snapshot
Current:  Camadas parciais, rotas gordas (models/routes/services/utils; regra de negócio nas rotas, services/utils mortos)
Target:   MVC: config / models / views(routes) / controllers / middlewares / composition root

================================
Total: 21 findings
================================
