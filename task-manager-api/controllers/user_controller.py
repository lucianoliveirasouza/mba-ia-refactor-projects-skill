import logging

from models.task import Task
from models.user import User
from utils.errors import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError

logger = logging.getLogger(__name__)


class UserController:
    def __init__(self, session):
        self._session = session

    def list_users_with_task_count(self):
        counts = Task.count_by_user()
        return [(user, counts.get(user.id, 0)) for user in User.list_all()]

    def get_user(self, user_id):
        user = User.get_by_id(user_id)
        if user is None:
            raise NotFoundError('Usuário não encontrado')
        return user

    def get_user_tasks(self, user_id):
        self.get_user(user_id)
        return Task.list_by_user(user_id)

    def create_user(self, data):
        self._ensure_email_available(data['email'])
        user = User(name=data['name'], email=data['email'], role=data['role'])
        user.set_password(data['password'])
        self._session.add(user)
        self._session.commit()
        logger.info('Usuário criado: id=%s', user.id)
        return user

    def update_user(self, user_id, changes):
        user = self.get_user(user_id)
        if 'email' in changes:
            self._ensure_email_available(changes['email'], current_user_id=user_id)
        password = changes.pop('password', None)
        for field, value in changes.items():
            setattr(user, field, value)
        if password is not None:
            user.set_password(password)
        self._session.commit()
        logger.info('Usuário atualizado: id=%s', user.id)
        return user

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        self._session.delete(user)  # tasks removidas pelo cascade do relacionamento
        self._session.commit()
        logger.info('Usuário deletado: id=%s', user_id)

    def authenticate(self, email, password):
        user = User.get_by_email(email)
        if user is None or not user.check_password(password):
            raise UnauthorizedError('Credenciais inválidas')
        if not user.active:
            raise ForbiddenError('Usuário inativo')
        return user

    @staticmethod
    def _ensure_email_available(email, current_user_id=None):
        existing = User.get_by_email(email)
        if existing is not None and existing.id != current_user_id:
            raise ConflictError('Email já cadastrado')
