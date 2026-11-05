"""Casos de uso de usuários e autenticação."""
import logging

from werkzeug.security import check_password_hash, generate_password_hash

from src.constants import TipoUsuario
from src.errors import ConflictError, NotFoundError, UnauthorizedError

logger = logging.getLogger(__name__)

CAMPOS_LOGIN = ("id", "nome", "email", "tipo")


class UsuarioController:
    def __init__(self, usuario_model):
        self.usuarios = usuario_model

    def listar(self):
        return self.usuarios.listar()

    def buscar(self, usuario_id):
        usuario = self.usuarios.buscar_por_id(usuario_id)
        if not usuario:
            raise NotFoundError("Usuário não encontrado")
        return usuario

    def criar(self, nome, email, senha):
        if self.usuarios.email_cadastrado(email):
            raise ConflictError("Email já cadastrado")
        usuario_id = self.usuarios.criar(nome, email, generate_password_hash(senha), TipoUsuario.CLIENTE)
        logger.info("Usuário criado com ID %s", usuario_id)
        return usuario_id

    def autenticar(self, email, senha):
        credenciais = self.usuarios.buscar_credenciais(email)
        if not credenciais or not check_password_hash(credenciais[1], senha):
            logger.info("Tentativa de login inválida")
            raise UnauthorizedError("Email ou senha inválidos")
        usuario = credenciais[0]
        logger.info("Login bem-sucedido do usuário %s", usuario["id"])
        return {campo: usuario[campo] for campo in CAMPOS_LOGIN}
