"""Operações de infraestrutura sobre o banco (health e administração)."""
import sqlite3

from src.errors import DatabaseError


class SistemaModel:
    def __init__(self, get_connection):
        self._conn = get_connection

    def contagens(self):
        try:
            row = self._conn().execute(
                """
                SELECT (SELECT COUNT(*) FROM produtos) AS produtos,
                       (SELECT COUNT(*) FROM usuarios) AS usuarios,
                       (SELECT COUNT(*) FROM pedidos) AS pedidos
                """
            ).fetchone()
        except sqlite3.Error as erro:
            raise DatabaseError(str(erro)) from erro
        return dict(row)

    def resetar(self):
        conn = self._conn()
        with conn:
            for tabela in ("itens_pedido", "pedidos", "produtos", "usuarios"):
                conn.execute(f"DELETE FROM {tabela}")  # nomes fixos (whitelist), sem dados externos

    def executar_sql(self, sql):
        """Executa SQL administrativo. Só é alcançável com token admin + flag explícita."""
        conn = self._conn()
        try:
            with conn:
                cursor = conn.execute(sql)
                linhas = cursor.fetchall() if cursor.description else None
        except sqlite3.Error as erro:
            raise DatabaseError(str(erro)) from erro
        return [dict(row) for row in linhas] if linhas is not None else None
