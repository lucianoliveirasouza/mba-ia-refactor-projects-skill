import re

from utils.constants import DEFAULT_COLOR
from utils.errors import ValidationError
from validators.common import optional_text, require_payload, required_text

COLOR_PATTERN = re.compile(r'^#[0-9a-fA-F]{6}$')


def _color(value):
    if not isinstance(value, str) or not COLOR_PATTERN.match(value):
        raise ValidationError('Cor inválida. Use o formato #RRGGBB')
    return value


def validate_category_create(data):
    data = require_payload(data)
    return {
        'name': required_text(data.get('name'), 'Nome é obrigatório'),
        'description': optional_text(data.get('description', ''), 'Descrição inválida'),
        'color': _color(data.get('color', DEFAULT_COLOR)),
    }


def validate_category_update(data):
    data = require_payload(data, allow_empty=True)
    cleaned = {}
    if 'name' in data:
        cleaned['name'] = required_text(data['name'], 'Nome é obrigatório')
    if 'description' in data:
        cleaned['description'] = optional_text(data['description'], 'Descrição inválida')
    if 'color' in data:
        cleaned['color'] = _color(data['color'])
    return cleaned
