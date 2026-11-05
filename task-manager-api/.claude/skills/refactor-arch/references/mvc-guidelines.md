# Guidelines de Arquitetura — MVC Alvo (Fase 3)

Em APIs HTTP, MVC é interpretado assim:

```
HTTP request
   │
   ▼
[ View / Route ]  ── valida e traduz o request, chama o controller, serializa a resposta
   │
   ▼
[ Controller ]    ── orquestra o caso de uso e aplica as regras de negócio
   │   (opcional: [ Service ] para regra de negócio grande ou integração externa)
   ▼
[ Model ]         ── entidades + acesso a dados (queries parametrizadas, transações)
   │
   ▼
[ Database ]

Transversais: [ Config ]  [ Middlewares: error handler, auth ]  [ Composition root ]
```

## Responsabilidades e regras por camada

### Config (`config/`)
- **Faz:** lê variáveis de ambiente (com `.env` opcional) e expõe um objeto/módulo de configuração; define defaults seguros apenas para desenvolvimento.
- **Não faz:** conter segredos reais; ser importado por models para decidir lógica de negócio.
- **Regra:** nenhum segredo, URI de banco, porta, flag de debug ou chave literal fora daqui. Crie `.env.example` documentando as variáveis.

### Models (`models/`)
- **Faz:** representa entidades e encapsula **todo** acesso a dados daquele domínio (CRUD, consultas, joins, transações). Retorna dados de domínio (objetos/dicts) — nunca objetos HTTP.
- **Não faz:** ler `request`, devolver `jsonify`/`res`, enviar e-mail, calcular desconto/faturamento ou decidir status de negócio.
- **Regras:** queries **sempre parametrizadas**; um arquivo por domínio (`product_model`, `user_model`…); sem N+1 (use JOIN/eager loading/agregações); escritas múltiplas em transação; conexão/sessão **recebida** (injeção) ou obtida via mecanismo do framework (ex.: `db.session` do Flask-SQLAlchemy, `g` por request) — nunca global mutável.
- Em projetos com ORM, a classe ORM é o model; métodos de domínio simples (`is_overdue`, `to_dict` sem dados sensíveis) podem ficar nela.

### Controllers (`controllers/`)
- **Faz:** implementa os casos de uso: recebe dados já extraídos do request (tipos primitivos/DTOs), aplica regras de negócio, coordena models e serviços, lança exceções de domínio (`NotFoundError`, `ValidationError`, `ConflictError`).
- **Não faz:** SQL direto; conhecer o objeto de request/response do framework (idealmente); formatar status HTTP.
- **Regra:** um controller por domínio. Se a regra de negócio for extensa ou houver integração externa (pagamento, e-mail), extraia para `services/` e injete no controller.

### Views / Routes (`views/` ou `routes/`)
- **Faz:** declara rotas (método + caminho), extrai e valida a entrada (body, params, query), chama o controller, converte o resultado em resposta HTTP (status + JSON) usando serializers/presenters.
- **Não faz:** regra de negócio, acesso a banco, `try/except` genérico (isso é do error handler).
- **Regra:** handlers curtos (idealmente < 15 linhas). Nomes de campos externos do contrato preservados aqui (mapeie `usr` → `name` na borda, se necessário).
- Em APIs JSON, a "View" é a camada de apresentação: rotas + serialização. Se o projeto renderiza templates, os templates também ficam aqui.

### Middlewares (`middlewares/`)
- **Error handler centralizado:** converte exceções de domínio em respostas HTTP padronizadas (`{"erro": msg}` ou `{"error": msg}` — mantenha a chave que o projeto já usava) e loga erros inesperados sem vazar stack trace ao cliente.
- **Auth/guard:** protege rotas administrativas/destrutivas (token via env, papel do usuário).
- Outros transversais: CORS configurado, logging de requests.

### Composition root (`app.py` / `app.js` / `server.js`)
- Cria a aplicação (preferir factory: `create_app(config)` / `createApp(deps)`), carrega config, inicializa banco, instancia models/services/controllers **injetando dependências**, registra rotas e middlewares, sobe o servidor.
- É o **único** lugar que conhece todas as implementações concretas.

## Direção de dependências

`routes → controllers → (services) → models → database`. Config e middlewares podem ser usados pelo composition root e pelas rotas. **Nunca** o inverso (model importando controller, controller importando rotas). Sem imports circulares.

## Estruturas alvo por stack

Adapte nomes ao idioma já usado no projeto (ex.: `produto_model.py` se o domínio é em português). Mantenha o comando de execução original.

### Python / Flask (projeto monolítico)
```
<projeto>/
├── app.py                      # entry point fino: from src.app import create_app; create_app().run(...)
├── requirements.txt
├── .env.example
└── src/
    ├── __init__.py
    ├── app.py                  # composition root: create_app()
    ├── config/
    │   ├── __init__.py
    │   └── settings.py
    ├── database/
    │   ├── __init__.py
    │   └── connection.py       # conexão por request (flask.g) + init_db/seed
    ├── models/                 # <dominio>_model.py
    ├── controllers/            # <dominio>_controller.py
    ├── services/               # (opcional) notification_service.py, pricing...
    ├── views/                  # <dominio>_routes.py (Blueprints) + serializers
    └── middlewares/
        ├── __init__.py
        ├── error_handler.py
        └── auth.py             # (se houver rotas admin)
```
Alternativa válida: manter os pacotes na raiz (sem `src/`) se o projeto já for assim — o importante são as camadas.

### Python / Flask (projeto já parcialmente organizado: `models/`, `routes/`, `services/`, `utils/`)
```
<projeto>/
├── app.py                      # composition root com create_app(); preserva `from app import app, db` se o seed usa
├── config/settings.py          # novo
├── database.py                 # mantém a instância db (ou database/__init__.py)
├── models/                     # mantém ORM; remove senha do to_dict; métodos de domínio reaproveitados
├── controllers/                # NOVO: regra de negócio que estava nas rotas
├── routes/                     # (= views) apenas HTTP: parse, validação, chamada ao controller
├── services/                   # integrações (e-mail) com config injetada
├── middlewares/error_handler.py
├── utils/                      # apenas helpers puros e constantes realmente usados
└── seed.py                     # atualizado se imports/hash mudarem
```

### Node.js / Express
```
<projeto>/
├── package.json                # "start" continua funcionando (ajuste "main"/"start" se mover o entry)
├── .env.example
└── src/
    ├── app.js                  # composition root: createApp() — monta express, deps, rotas, middlewares
    ├── server.js               # (opcional) listen; ou listen no app.js se "start" aponta para ele
    ├── config/
    │   └── index.js            # process.env com defaults de dev
    ├── database/
    │   └── connection.js       # abre o banco, wrapper Promise (run/get/all), schema + seed
    ├── models/                 # <dominio>Model.js — queries parametrizadas, async
    ├── controllers/            # <dominio>Controller.js — casos de uso
    ├── services/               # paymentService.js, etc.
    ├── routes/                 # (= views) <dominio>Routes.js com express.Router()
    └── middlewares/
        ├── errorHandler.js
        ├── asyncHandler.js     # Express 4 não captura rejeições de async handlers
        └── auth.js
```

## Projetos parcialmente organizados

Já ter pastas não significa estar correto. Evolua em vez de reescrever:
1. Mantenha os models ORM; mova para eles (ou para controllers) a lógica de domínio duplicada nas rotas.
2. Crie `controllers/` e esvazie as rotas de regra de negócio (estatísticas, cálculos, cascatas de delete).
3. Centralize validação (schemas/validators) e listas de valores válidos (constantes/enums únicos).
4. Substitua `try/except` por rota por error handler central + exceções de domínio.
5. Ligue services existentes que estavam sem uso, injetando config em vez de credenciais literais.
6. Remova helpers mortos ou passe a usá-los.

## Preservação do contrato (obrigatório)

- Mesmas rotas (inclusive prefixos e ordem quando há conflito estático/dinâmico), mesmos métodos.
- Mesmos nomes de campos no request e no response e mesmos status HTTP de sucesso/erro esperados.
- Mesma porta e mesmo comando de execução; scripts auxiliares (seed) continuam funcionando.
- Exceções permitidas (documentar no resumo): remoção de dados sensíveis das respostas (senha, hash, secret), proteção de endpoints perigosos (passam a responder 401/403 sem credencial), correção de bug que gerava 500.

## Critérios de "pronto"

- [ ] Nenhum segredo/configuração literal fora de `config/`
- [ ] Nenhum SQL fora de models; todo SQL parametrizado
- [ ] Rotas sem regra de negócio e sem acesso a banco
- [ ] Controllers sem SQL e sem objetos HTTP
- [ ] Error handler central; nenhum `except:`/`catch` genérico devolvendo `str(e)`
- [ ] Sem estado global mutável; dependências injetadas no composition root
- [ ] Entry point claro e comando original funcionando
- [ ] App sobe e todos os endpoints do inventário respondem como na baseline
