import logging

from models.category import Category
from models.task import Task
from utils.errors import NotFoundError

logger = logging.getLogger(__name__)


class CategoryController:
    def __init__(self, session):
        self._session = session

    def list_categories_with_task_count(self):
        counts = Task.count_by_category()
        return [(category, counts.get(category.id, 0)) for category in Category.list_all()]

    def get_category(self, category_id):
        category = Category.get_by_id(category_id)
        if category is None:
            raise NotFoundError('Categoria não encontrada')
        return category

    def create_category(self, data):
        category = Category(**data)
        self._session.add(category)
        self._session.commit()
        logger.info('Categoria criada: id=%s', category.id)
        return category

    def update_category(self, category_id, changes):
        category = self.get_category(category_id)
        for field, value in changes.items():
            setattr(category, field, value)
        self._session.commit()
        return category

    def delete_category(self, category_id):
        category = self.get_category(category_id)
        # O relacionamento desvincula as tasks (category_id = NULL) no mesmo commit.
        self._session.delete(category)
        self._session.commit()
        logger.info('Categoria deletada: id=%s', category_id)
