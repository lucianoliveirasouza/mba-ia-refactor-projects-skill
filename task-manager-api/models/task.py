from sqlalchemy import case, func
from sqlalchemy.orm import joinedload

from database import db
from utils.constants import DEFAULT_PRIORITY, TaskStatus
from utils.helpers import utcnow


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=TaskStatus.PENDING)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', back_populates='tasks')
    category = db.relationship('Category', back_populates='tasks')

    # ---- domínio -------------------------------------------------------

    def to_dict(self):
        data = {}
        data['id'] = self.id
        data['title'] = self.title
        data['description'] = self.description
        data['status'] = self.status
        data['priority'] = self.priority
        data['user_id'] = self.user_id
        data['category_id'] = self.category_id
        data['created_at'] = str(self.created_at)
        data['updated_at'] = str(self.updated_at)
        data['due_date'] = str(self.due_date) if self.due_date else None
        data['tags'] = self.tags.split(',') if self.tags else []
        return data

    def is_overdue(self, now=None):
        now = now or utcnow()
        return self.due_date is not None and self.due_date < now and self.status not in TaskStatus.CLOSED

    # ---- acesso a dados ------------------------------------------------

    @classmethod
    def get_by_id(cls, task_id):
        return db.session.get(cls, task_id)

    @classmethod
    def list_all(cls, with_relations=False):
        stmt = db.select(cls).order_by(cls.id)
        if with_relations:
            stmt = stmt.options(joinedload(cls.user), joinedload(cls.category))
        return db.session.execute(stmt).scalars().all()

    @classmethod
    def list_by_user(cls, user_id):
        stmt = db.select(cls).where(cls.user_id == user_id).order_by(cls.id)
        return db.session.execute(stmt).scalars().all()

    @classmethod
    def search(cls, text=None, status=None, priority=None, user_id=None):
        stmt = db.select(cls)
        if text:
            pattern = f'%{text}%'
            stmt = stmt.where(db.or_(cls.title.like(pattern), cls.description.like(pattern)))
        if status:
            stmt = stmt.where(cls.status == status)
        if priority is not None:
            stmt = stmt.where(cls.priority == priority)
        if user_id is not None:
            stmt = stmt.where(cls.user_id == user_id)
        return db.session.execute(stmt.order_by(cls.id)).scalars().all()

    @classmethod
    def count_all(cls):
        return db.session.scalar(db.select(func.count(cls.id)))

    @classmethod
    def count_by_status(cls):
        rows = db.session.execute(db.select(cls.status, func.count(cls.id)).group_by(cls.status)).all()
        return {status: count for status, count in rows}

    @classmethod
    def count_by_priority(cls):
        rows = db.session.execute(db.select(cls.priority, func.count(cls.id)).group_by(cls.priority)).all()
        return {priority: count for priority, count in rows}

    @classmethod
    def count_by_user(cls):
        rows = db.session.execute(
            db.select(cls.user_id, func.count(cls.id)).where(cls.user_id.is_not(None)).group_by(cls.user_id)
        ).all()
        return {user_id: count for user_id, count in rows}

    @classmethod
    def count_by_category(cls):
        rows = db.session.execute(
            db.select(cls.category_id, func.count(cls.id))
            .where(cls.category_id.is_not(None))
            .group_by(cls.category_id)
        ).all()
        return {category_id: count for category_id, count in rows}

    @classmethod
    def completion_by_user(cls):
        """{user_id: (total, concluídas)} em uma única query."""
        done = func.sum(case((cls.status == TaskStatus.DONE, 1), else_=0))
        rows = db.session.execute(
            db.select(cls.user_id, func.count(cls.id), done).where(cls.user_id.is_not(None)).group_by(cls.user_id)
        ).all()
        return {user_id: (total, int(done_count or 0)) for user_id, total, done_count in rows}

    @classmethod
    def _overdue_filter(cls, now):
        return db.and_(cls.due_date.is_not(None), cls.due_date < now, cls.status.not_in(TaskStatus.CLOSED))

    @classmethod
    def list_overdue(cls, now):
        stmt = db.select(cls).where(cls._overdue_filter(now)).order_by(cls.id)
        return db.session.execute(stmt).scalars().all()

    @classmethod
    def count_overdue(cls, now):
        return db.session.scalar(db.select(func.count(cls.id)).where(cls._overdue_filter(now)))

    @classmethod
    def count_created_since(cls, since):
        return db.session.scalar(db.select(func.count(cls.id)).where(cls.created_at >= since))

    @classmethod
    def count_completed_since(cls, since):
        return db.session.scalar(
            db.select(func.count(cls.id)).where(cls.status == TaskStatus.DONE, cls.updated_at >= since)
        )
