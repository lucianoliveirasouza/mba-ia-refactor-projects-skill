# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Notas da refatoração (refactor-arch)

- O projeto foi refatorado para MVC (ver *Estrutura* abaixo).
- A porta é configurável via `PORT`. O banco fica em `instance/tasks.db` (padrão do Flask-SQLAlchemy para URIs SQLite relativas).
- As senhas agora são gravadas com hash seguro. Se o banco foi criado pela versão anterior (senhas em MD5), rode `python seed.py` novamente.

## Configuração

Todas as variáveis estão documentadas em `.env.example` (opcional: `cp .env.example .env` e ajuste `SECRET_KEY`, `PORT`, `CORS_ORIGINS`, `SMTP_*`). As principais:

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
