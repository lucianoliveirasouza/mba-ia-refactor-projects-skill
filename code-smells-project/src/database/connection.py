"""Conexão SQLite por requisição (flask.g), sem estado global mutável."""
import sqlite3

from flask import current_app, g

from src.database.schema import create_schema
from src.database.seed import migrar_senhas_legadas, seed_if_empty


def _connect(database_path):
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_connection():
    if "db" not in g:
        g.db = _connect(current_app.config["DATABASE_PATH"])
    return g.db


def close_connection(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_app(app):
    """Registra o ciclo de vida da conexão e prepara o banco (schema + seed) no boot."""
    app.teardown_appcontext(close_connection)
    conn = _connect(app.config["DATABASE_PATH"])
    try:
        create_schema(conn)
        seed_if_empty(conn)
        migrar_senhas_legadas(conn)
    finally:
        conn.close()
