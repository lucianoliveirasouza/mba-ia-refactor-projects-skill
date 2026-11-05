"""Exceções de domínio. O error handler central as converte em respostas HTTP."""


class AppError(Exception):
    status = 400

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    status = 400


class UnauthorizedError(AppError):
    status = 401


class ForbiddenError(AppError):
    status = 403


class NotFoundError(AppError):
    status = 404


class ConflictError(AppError):
    status = 409


class DatabaseError(Exception):
    """Falha de acesso ao banco, traduzida pelo model para não vazar o driver às camadas acima."""


class EstoqueInsuficienteError(Exception):
    """Lançada pelo model quando a baixa condicional de estoque não pode ser aplicada."""

    def __init__(self, produto_id):
        super().__init__(produto_id)
        self.produto_id = produto_id
