"""Serialização das respostas HTTP (camada de apresentação)."""
from utils.helpers import utcnow

TASK_SUMMARY_FIELDS = ('id', 'title', 'description', 'status', 'priority', 'created_at', 'due_date')


def serialize_task(task, *, overdue=False, relations=False, now=None):
    data = task.to_dict()
    if overdue:
        data['overdue'] = task.is_overdue(now or utcnow())
    if relations:
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
    return data


def serialize_task_summary(task, now=None):
    full = task.to_dict()
    data = {field: full[field] for field in TASK_SUMMARY_FIELDS}
    data['overdue'] = task.is_overdue(now or utcnow())
    return data


def serialize_user(user):
    return user.to_dict()


def serialize_category(category):
    return category.to_dict()
