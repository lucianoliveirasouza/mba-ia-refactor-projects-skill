# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo (senhas gravadas como hash). Bancos criados pela versão anterior, com senhas em texto puro, são migrados para hash automaticamente no boot.

## Configuração

Todas as variáveis são opcionais. Veja `.env.example`:

| Variável | Default | Descrição |
|---|---|---|
| `SECRET_KEY` | aleatória por boot | Chave de sessão do Flask |
| `FLASK_DEBUG` | `false` | Modo debug (não habilite exposto na rede) |
| `APP_ENV` | `development` | Ambiente exibido no `/health` |
| `HOST` / `PORT` | `0.0.0.0` / `5000` | Endereço do servidor |
| `DATABASE_PATH` | `loja.db` | Arquivo SQLite |
| `CORS_ORIGINS` | `*` | Origens permitidas, separadas por vírgula |
| `ADMIN_TOKEN` | vazio | Token do header `X-Admin-Token` para `/admin/*` (vazio = bloqueado, 403) |
| `ENABLE_ADMIN_QUERY` | `false` | Habilita `/admin/query` (requer também `ADMIN_TOKEN`) |
| `LOG_LEVEL` | `INFO` | Nível de log |

## Estrutura

```
app.py              entry point
src/app.py          composition root (create_app)
src/config/         configuração via ambiente
src/database/       conexão por request, schema, seed
src/models/         acesso a dados por domínio
src/controllers/    casos de uso e regras de negócio
src/services/       notificações
src/views/          rotas (Blueprints) e validação de entrada
src/middlewares/    error handler e proteção admin
```
