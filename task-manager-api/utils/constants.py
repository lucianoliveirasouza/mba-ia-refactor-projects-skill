"""Constantes de domínio compartilhadas por models, validators e controllers."""


class TaskStatus:
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'
    CANCELLED = 'cancelled'

    ALL = (PENDING, IN_PROGRESS, DONE, CANCELLED)
    CLOSED = (DONE, CANCELLED)


class Role:
    USER = 'user'
    ADMIN = 'admin'
    MANAGER = 'manager'

    ALL = (USER, ADMIN, MANAGER)


TITLE_MIN_LENGTH = 3
TITLE_MAX_LENGTH = 200

PRIORITY_MIN = 1
PRIORITY_MAX = 5
DEFAULT_PRIORITY = 3
HIGH_PRIORITY_THRESHOLD = 2  # prioridades 1 e 2 contam como "alta"

# Rótulos usados no relatório geral (prioridade -> chave da resposta)
PRIORITY_LABELS = {
    1: 'critical',
    2: 'high',
    3: 'medium',
    4: 'low',
    5: 'minimal',
}

MIN_PASSWORD_LENGTH = 4
DEFAULT_COLOR = '#000000'
DATE_FORMAT = '%Y-%m-%d'
RECENT_ACTIVITY_DAYS = 7
