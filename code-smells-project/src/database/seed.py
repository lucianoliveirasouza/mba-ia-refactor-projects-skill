"""Dados iniciais (executado no boot quando o catálogo está vazio)."""
import logging

from werkzeug.security import generate_password_hash

from src.constants import TipoUsuario

logger = logging.getLogger(__name__)

PRODUTOS_INICIAIS = (
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
)

# Credenciais de demonstração; gravadas apenas como hash.
USUARIOS_INICIAIS = (
    ("Admin", "admin@loja.com", "admin123", TipoUsuario.ADMIN),
    ("João Silva", "joao@email.com", "123456", TipoUsuario.CLIENTE),
    ("Maria Santos", "maria@email.com", "senha123", TipoUsuario.CLIENTE),
)

_PREFIXOS_HASH = ("scrypt:", "pbkdf2:")


def seed_if_empty(conn):
    (total_produtos,) = conn.execute("SELECT COUNT(*) FROM produtos").fetchone()
    if total_produtos:
        return
    with conn:
        conn.executemany(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            PRODUTOS_INICIAIS,
        )
        conn.executemany(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            [(nome, email, generate_password_hash(senha), tipo) for nome, email, senha, tipo in USUARIOS_INICIAIS],
        )
    logger.info("Banco populado com dados iniciais")


def migrar_senhas_legadas(conn):
    """Converte senhas em texto puro de bancos criados pela versão anterior para hash."""
    rows = conn.execute("SELECT id, senha FROM usuarios").fetchall()
    legadas = [
        (generate_password_hash(row["senha"]), row["id"])
        for row in rows
        if row["senha"] and not row["senha"].startswith(_PREFIXOS_HASH)
    ]
    if legadas:
        with conn:
            conn.executemany("UPDATE usuarios SET senha = ? WHERE id = ?", legadas)
        logger.info("%d senha(s) legada(s) convertida(s) para hash", len(legadas))
