"""Script para popular o banco com dados iniciais."""
from datetime import timedelta

from app import create_app
from database import db
from models import Category, Task, User
from utils.constants import Role, TaskStatus
from utils.helpers import utcnow

USERS = [
    {'name': 'João Silva', 'email': 'joao@email.com', 'password': '1234', 'role': Role.ADMIN},
    {'name': 'Maria Santos', 'email': 'maria@email.com', 'password': 'abcd', 'role': Role.USER},
    {'name': 'Pedro Oliveira', 'email': 'pedro@email.com', 'password': 'pass', 'role': Role.MANAGER},
]

CATEGORIES = [
    {'name': 'Backend', 'description': 'Tarefas de backend', 'color': '#3498db'},
    {'name': 'Frontend', 'description': 'Tarefas de frontend', 'color': '#2ecc71'},
    {'name': 'DevOps', 'description': 'Tarefas de infraestrutura', 'color': '#e74c3c'},
    {'name': 'Bug', 'description': 'Correção de bugs', 'color': '#e67e22'},
]


def build_tasks(users, categories, now):
    u1, u2, u3 = users
    backend, frontend, devops, bug = categories
    return [
        {'title': 'Implementar autenticação JWT', 'description': 'Adicionar autenticação real com JWT', 'status': TaskStatus.PENDING, 'priority': 1, 'user_id': u1.id, 'category_id': backend.id, 'due_date': now - timedelta(days=3)},
        {'title': 'Criar tela de login', 'description': 'Tela de login responsiva', 'status': TaskStatus.IN_PROGRESS, 'priority': 2, 'user_id': u2.id, 'category_id': frontend.id, 'due_date': now + timedelta(days=5)},
        {'title': 'Configurar CI/CD', 'description': 'Pipeline com GitHub Actions', 'status': TaskStatus.DONE, 'priority': 2, 'user_id': u3.id, 'category_id': devops.id, 'tags': 'devops,ci,github'},
        {'title': 'Corrigir bug no filtro de busca', 'description': 'Filtro não funciona com caracteres especiais', 'status': TaskStatus.PENDING, 'priority': 1, 'user_id': u1.id, 'category_id': bug.id, 'due_date': now - timedelta(days=1)},
        {'title': 'Adicionar paginação na API', 'description': 'Endpoints retornam todos os registros', 'status': TaskStatus.PENDING, 'priority': 3, 'user_id': u1.id, 'category_id': backend.id, 'due_date': now + timedelta(days=10)},
        {'title': 'Escrever testes unitários', 'description': 'Cobertura mínima de 80%', 'status': TaskStatus.PENDING, 'priority': 2, 'user_id': u2.id, 'category_id': backend.id},
        {'title': 'Documentar API com Swagger', 'description': 'Gerar documentação automática', 'status': TaskStatus.CANCELLED, 'priority': 4, 'user_id': u3.id, 'category_id': backend.id},
        {'title': 'Refatorar models', 'description': 'Melhorar organização dos models', 'status': TaskStatus.IN_PROGRESS, 'priority': 3, 'user_id': u2.id, 'category_id': backend.id, 'tags': 'refactor,tech-debt'},
        {'title': 'Configurar monitoramento', 'description': 'Prometheus + Grafana', 'status': TaskStatus.PENDING, 'priority': 4, 'user_id': u3.id, 'category_id': devops.id, 'due_date': now + timedelta(days=20)},
        {'title': 'Melhorar validações de input', 'description': 'Usar marshmallow ou pydantic', 'status': TaskStatus.PENDING, 'priority': 3, 'user_id': u1.id, 'category_id': backend.id, 'tags': 'improvement,validation'},
    ]


def seed_data():
    app = create_app()
    with app.app_context():
        db.session.execute(db.delete(Task))
        db.session.execute(db.delete(User))
        db.session.execute(db.delete(Category))

        users = []
        for data in USERS:
            user = User(name=data['name'], email=data['email'], role=data['role'])
            user.set_password(data['password'])
            users.append(user)
        categories = [Category(**data) for data in CATEGORIES]
        db.session.add_all(users + categories)
        db.session.flush()  # gera os IDs antes de vincular as tasks, preservando a ordem de inserção

        db.session.add_all([Task(**data) for data in build_tasks(users, categories, utcnow())])
        db.session.commit()

        print('Seed concluído com sucesso!')
        print(f'  {User.count_all()} usuários')
        print(f'  {Category.count_all()} categorias')
        print(f'  {Task.count_all()} tasks')


if __name__ == '__main__':
    seed_data()
