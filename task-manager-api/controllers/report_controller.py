from datetime import timedelta

from models.category import Category
from models.task import Task
from models.user import User
from utils.constants import HIGH_PRIORITY_THRESHOLD, PRIORITY_LABELS, RECENT_ACTIVITY_DAYS, TaskStatus
from utils.errors import NotFoundError
from utils.helpers import calculate_percentage, utcnow


class ReportController:
    def summary(self):
        now = utcnow()
        since = now - timedelta(days=RECENT_ACTIVITY_DAYS)
        by_status = Task.count_by_status()
        by_priority = Task.count_by_priority()
        overdue_tasks = Task.list_overdue(now)
        completion = Task.completion_by_user()

        user_productivity = []
        for user in User.list_all():
            total, completed = completion.get(user.id, (0, 0))
            user_productivity.append({
                'user_id': user.id,
                'user_name': user.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': calculate_percentage(completed, total),
            })

        return {
            'generated_at': str(now),
            'overview': {
                'total_tasks': Task.count_all(),
                'total_users': User.count_all(),
                'total_categories': Category.count_all(),
            },
            'tasks_by_status': {status: by_status.get(status, 0) for status in TaskStatus.ALL},
            'tasks_by_priority': {label: by_priority.get(priority, 0) for priority, label in PRIORITY_LABELS.items()},
            'overdue': {
                'count': len(overdue_tasks),
                'tasks': [
                    {
                        'id': task.id,
                        'title': task.title,
                        'due_date': str(task.due_date),
                        'days_overdue': (now - task.due_date).days,
                    }
                    for task in overdue_tasks
                ],
            },
            'recent_activity': {
                'tasks_created_last_7_days': Task.count_created_since(since),
                'tasks_completed_last_7_days': Task.count_completed_since(since),
            },
            'user_productivity': user_productivity,
        }

    def user_report(self, user_id):
        user = User.get_by_id(user_id)
        if user is None:
            raise NotFoundError('Usuário não encontrado')

        now = utcnow()
        tasks = Task.list_by_user(user_id)
        by_status = {status: 0 for status in TaskStatus.ALL}
        for task in tasks:
            if task.status in by_status:
                by_status[task.status] += 1
        total = len(tasks)

        return {
            'user': {'id': user.id, 'name': user.name, 'email': user.email},
            'statistics': {
                'total_tasks': total,
                **by_status,
                'overdue': sum(1 for task in tasks if task.is_overdue(now)),
                'high_priority': sum(1 for task in tasks if task.priority <= HIGH_PRIORITY_THRESHOLD),
                'completion_rate': calculate_percentage(by_status[TaskStatus.DONE], total),
            },
        }
