from utils.constants import (
    DATE_FORMAT,
    DEFAULT_PRIORITY,
    PRIORITY_MAX,
    PRIORITY_MIN,
    TITLE_MAX_LENGTH,
    TITLE_MIN_LENGTH,
    TaskStatus,
)
from utils.errors import ValidationError
from utils.helpers import parse_date
from validators.common import optional_id, optional_text, require_payload, required_text


def _title(value):
    title = required_text(value, 'Título é obrigatório')
    if len(title) < TITLE_MIN_LENGTH:
        raise ValidationError('Título muito curto')
    if len(title) > TITLE_MAX_LENGTH:
        raise ValidationError('Título muito longo')
    return title


def _status(value):
    if value not in TaskStatus.ALL:
        raise ValidationError('Status inválido')
    return value


def _priority(value):
    if isinstance(value, bool):
        raise ValidationError('Prioridade inválida')
    try:
        priority = int(value)
    except (TypeError, ValueError):
        raise ValidationError('Prioridade inválida') from None
    if not PRIORITY_MIN <= priority <= PRIORITY_MAX:
        raise ValidationError(f'Prioridade deve ser entre {PRIORITY_MIN} e {PRIORITY_MAX}')
    return priority


def _due_date(value):
    if not value:
        return None
    parsed = parse_date(value, DATE_FORMAT) if isinstance(value, str) else None
    if parsed is None:
        raise ValidationError('Formato de data inválido. Use YYYY-MM-DD')
    return parsed


def _tags(value):
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, list) and all(isinstance(tag, str) for tag in value):
        return ','.join(value)
    raise ValidationError('Tags inválidas')


_FIELD_VALIDATORS = {
    'title': _title,
    'description': lambda value: optional_text(value, 'Descrição inválida'),
    'status': _status,
    'priority': _priority,
    'user_id': lambda value: optional_id(value, 'user_id inválido'),
    'category_id': lambda value: optional_id(value, 'category_id inválido'),
    'due_date': _due_date,
    'tags': _tags,
}


def validate_task_create(data):
    data = require_payload(data)
    return {
        'title': _title(data.get('title')),
        'description': optional_text(data.get('description', ''), 'Descrição inválida'),
        'status': _status(data.get('status', TaskStatus.PENDING)),
        'priority': _priority(data.get('priority', DEFAULT_PRIORITY)),
        'user_id': optional_id(data.get('user_id'), 'user_id inválido'),
        'category_id': optional_id(data.get('category_id'), 'category_id inválido'),
        'due_date': _due_date(data.get('due_date')),
        'tags': _tags(data.get('tags')) or None,
    }


def validate_task_update(data):
    data = require_payload(data)
    return {field: validate(data[field]) for field, validate in _FIELD_VALIDATORS.items() if field in data}


def validate_search_params(args):
    priority = args.get('priority', '')
    user_id = args.get('user_id', '')
    return {
        'text': args.get('q', ''),
        'status': args.get('status', ''),
        'priority': _priority(priority) if priority else None,
        'user_id': optional_id(user_id, 'user_id inválido') if user_id else None,
    }
