"""Acesso a dados de usuários. A senha (hash) nunca sai deste módulo nas listagens."""

CAMPOS_PUBLICOS_USUARIO = ("id", "nome", "email", "tipo", "criado_em")
_SELECT_PUBLICO = f"SELECT {', '.join(CAMPOS_PUBLICOS_USUARIO)} FROM usuarios"


def _row_to_usuario(row):
    return {campo: row[campo] for campo in CAMPOS_PUBLICOS_USUARIO}


class UsuarioModel:
    def __init__(self, get_connection):
        self._conn = get_connection

    def listar(self):
        rows = self._conn().execute(_SELECT_PUBLICO).fetchall()
        return [_row_to_usuario(row) for row in rows]

    def buscar_por_id(self, usuario_id):
        row = self._conn().execute(f"{_SELECT_PUBLICO} WHERE id = ?", (usuario_id,)).fetchone()
        return _row_to_usuario(row) if row else None

    def existe(self, usuario_id):
        return self._conn().execute("SELECT 1 FROM usuarios WHERE id = ?", (usuario_id,)).fetchone() is not None

    def email_cadastrado(self, email):
        return self._conn().execute("SELECT 1 FROM usuarios WHERE email = ?", (email,)).fetchone() is not None

    def buscar_credenciais(self, email):
        """Retorna os dados públicos + o hash da senha (uso exclusivo da autenticação)."""
        row = self._conn().execute(
            f"SELECT {', '.join(CAMPOS_PUBLICOS_USUARIO)}, senha FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
        if not row:
            return None
        return _row_to_usuario(row), row["senha"]

    def criar(self, nome, email, senha_hash, tipo):
        conn = self._conn()
        with conn:
            cursor = conn.execute(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                (nome, email, senha_hash, tipo),
            )
        return cursor.lastrowid
