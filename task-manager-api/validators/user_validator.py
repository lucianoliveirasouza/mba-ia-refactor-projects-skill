import re

from utils.constants import MIN_PASSWORD_LENGTH, Role
from utils.errors import ValidationError
from validators.common import require_payload, required_text

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')


def _email(value):
    if not isinstance(value, str) or not EMAIL_PATTERN.match(value):
        raise ValidationError('Email inválido')
    return value


def _password(value, message):
    if not isinstance(value, str) or len(value) < MIN_PASSWORD_LENGTH:
        raise ValidationError(message)
    return value


def _role(value):
    if value not in Role.ALL:
        raise ValidationError('Role inválido')
    return value


def validate_user_create(data):
    data = require_payload(data)
    name = required_text(data.get('name'), 'Nome é obrigatório')
    if not data.get('email'):
        raise ValidationError('Email é obrigatório')
    if not data.get('password'):
        raise ValidationError('Senha é obrigatória')
    return {
        'name': name,
        'email': _email(data['email']),
        'password': _password(data['password'], f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres'),
        'role': _role(data.get('role', Role.USER)),
    }


def validate_user_update(data):
    data = require_payload(data)
    cleaned = {}
    if 'name' in data:
        cleaned['name'] = required_text(data['name'], 'Nome é obrigatório')
    if 'email' in data:
        cleaned['email'] = _email(data['email'])
    if 'password' in data:
        cleaned['password'] = _password(data['password'], 'Senha muito curta')
    if 'role' in data:
        cleaned['role'] = _role(data['role'])
    if 'active' in data:
        if not isinstance(data['active'], bool):
            raise ValidationError('Campo active deve ser booleano')
        cleaned['active'] = data['active']
    return cleaned


def validate_login(data):
    data = require_payload(data)
    email, password = data.get('email'), data.get('password')
    if not email or not password:
        raise ValidationError('Email e senha são obrigatórios')
    return {'email': email, 'password': password}
