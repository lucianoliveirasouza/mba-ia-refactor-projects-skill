"""Helpers puros (sem dependência de Flask ou do banco)."""
from datetime import datetime, timezone


def utcnow():
    """UTC atual como datetime *naive*, compatível com os valores já gravados no banco."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def parse_date(value, fmt):
    try:
        return datetime.strptime(value, fmt)
    except (TypeError, ValueError):
        return None
