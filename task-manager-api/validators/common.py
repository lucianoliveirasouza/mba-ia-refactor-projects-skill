from utils.errors import ValidationError


def require_payload(data, allow_empty=False):
    if not isinstance(data, dict) or (not data and not allow_empty):
        raise ValidationError('Dados inválidos')
    return data


def optional_text(value, message):
    if value is not None and not isinstance(value, str):
        raise ValidationError(message)
    return value


def required_text(value, message):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(message)
    return value.strip()


def optional_id(value, message):
    """IDs de relacionamento: vazio/None desvincula; caso contrário precisa ser inteiro."""
    if value in (None, '', 0):
        return None
    if isinstance(value, bool):
        raise ValidationError(message)
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(message) from None
