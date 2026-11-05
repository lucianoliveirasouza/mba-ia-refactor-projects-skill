# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`, já refatorada para MVC.

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # opcional: ajuste SECRET_KEY, PORT, CORS_ORIGINS, SMTP_*
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000` (porta configurável via `PORT`). O `seed.py` recria o banco SQLite (`instance/tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot** (e novamente se o banco foi criado pela versão anterior, que gravava senhas em MD5).

## Configuração

Todas as variáveis estão documentadas em `.env.example`. As principais:

| Variável | Default (dev) | Uso |
|---|---|---|
| `SECRET_KEY` | `dev-only-change-me` | Assina os tokens de login — **defina em produção** |
| `DATABASE_URL` | `sqlite:///tasks.db` | URI do SQLAlchemy |
| `HOST` / `PORT` | `0.0.0.0` / `5000` | Endereço do servidor |
| `FLASK_DEBUG` | `false` | Debugger do Werkzeug (nunca em produção) |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Origens permitidas (`*` libera todas) |
| `SMTP_HOST` … | vazio | Notificação por email ao atribuir tasks (vazio = só log) |

## Autenticação

`POST /login` devolve um `token` assinado. Envie-o como `Authorization: Bearer <token>` nas operações administrativas:

- `DELETE /users/<id>`
- `POST /users` com `role` diferente de `user`
- `PUT /users/<id>` alterando `role`

Sem token → `401`; usuário não-admin → `403`.

## Estrutura

```
app.py            composition root (create_app)
config/           settings lidos do ambiente
database.py       instância do SQLAlchemy
models/           entidades ORM + acesso a dados
controllers/      regras de negócio / casos de uso
routes/           views HTTP (blueprints) + serializers
validators/       validação de entrada
middlewares/      error handler central e auth
services/         integrações (email)
utils/            constantes, exceções de domínio e helpers puros
```
