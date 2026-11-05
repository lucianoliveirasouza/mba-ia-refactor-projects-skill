import logging

from models.category import Category
from models.task import Task
from models.user import User
from utils.constants import TaskStatus
from utils.errors import NotFoundError
from utils.helpers import calculate_percentage, utcnow

logger = logging.getLogger(__name__)


class TaskController:
    def __init__(self, session, notifier):
        self._session = session
        self._notifier = notifier

    def list_tasks(self):
        return Task.list_all(with_relations=True)

    def get_task(self, task_id):
        task = Task.get_by_id(task_id)
        if task is None:
            raise NotFoundError('Task não encontrada')
        return task

    def search_tasks(self, text, status, priority, user_id):
        return Task.search(text=text, status=status, priority=priority, user_id=user_id)

    def create_task(self, data):
        assignee = self._ensure_user(data['user_id'])
        self._ensure_category(data['category_id'])

        task = Task(**data)
        self._session.add(task)
        self._session.commit()
        logger.info('Task criada: id=%s', task.id)

        if assignee is not None:
            self._notifier.notify_task_assigned(assignee, task)
        return task

    def update_task(self, task_id, changes):
        task = self.get_task(task_id)
        new_assignee = None
        if 'user_id' in changes:
            new_assignee = self._ensure_user(changes['user_id'])
            if changes['user_id'] == task.user_id:
                new_assignee = None
        if 'category_id' in changes:
            self._ensure_category(changes['category_id'])

        for field, value in changes.items():
            setattr(task, field, value)
        task.updated_at = utcnow()
        self._session.commit()
        logger.info('Task atualizada: id=%s', task.id)

        if new_assignee is not None:
            self._notifier.notify_task_assigned(new_assignee, task)
        return task

    def delete_task(self, task_id):
        task = self.get_task(task_id)
        self._session.delete(task)
        self._session.commit()
        logger.info('Task deletada: id=%s', task_id)

    def stats(self):
        total = Task.count_all()
        by_status = Task.count_by_status()
        done = by_status.get(TaskStatus.DONE, 0)
        return {
            'total': total,
            **{status: by_status.get(status, 0) for status in TaskStatus.ALL},
            'overdue': Task.count_overdue(utcnow()),
            'completion_rate': calculate_percentage(done, total),
        }

    @staticmethod
    def _ensure_user(user_id):
        if user_id is None:
            return None
        user = User.get_by_id(user_id)
        if user is None:
            raise NotFoundError('Usuário não encontrado')
        return user

    @staticmethod
    def _ensure_category(category_id):
        if category_id is not None and Category.get_by_id(category_id) is None:
            raise NotFoundError('Categoria não encontrada')
