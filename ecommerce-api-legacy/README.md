# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

### Configuração

Variáveis de ambiente (veja `.env.example`; um `.env` na raiz é carregado automaticamente):

| Variável | Padrão | Descrição |
|---|---|---|
| `PORT` | `3000` | Porta HTTP |
| `DB_PATH` | `:memory:` | Banco SQLite |
| `PAYMENT_GATEWAY_KEY` | vazio | Chave do gateway (nunca é logada) |
| `ADMIN_TOKEN` | vazio | Token exigido no header `X-Admin-Token` em `GET /api/admin/financial-report` e `DELETE /api/users/:id`. Vazio = rotas bloqueadas |
| `LOG_LEVEL` | `info` | `debug`, `info`, `warn`, `error`, `silent` |

```bash
ADMIN_TOKEN=dev-admin-token npm start
```

### Arquitetura

`src/app.js` (composition root) → `routes/` (HTTP + validação) → `controllers/` (casos de uso) → `services/` (pagamento) → `models/` (SQL parametrizado) → `database/` (conexão, schema e seed). Transversais: `config/`, `middlewares/` (auth, error handler), `errors/`, `utils/`.
