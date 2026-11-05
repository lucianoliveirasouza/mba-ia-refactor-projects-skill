"""Composition root: cria a app, carrega config, injeta dependências e registra rotas."""
import logging

from flask import Flask
from flask_cors import CORS

from src import database
from src.config import Settings
from src.controllers.pedido_controller import PedidoController
from src.controllers.produto_controller import ProdutoController
from src.controllers.relatorio_controller import RelatorioController
from src.controllers.sistema_controller import SistemaController
from src.controllers.usuario_controller import UsuarioController
from src.middlewares.error_handler import register_error_handlers
from src.models.pedido_model import PedidoModel
from src.models.produto_model import ProdutoModel
from src.models.sistema_model import SistemaModel
from src.models.usuario_model import UsuarioModel
from src.services.notification_service import NotificationService
from src.views.pedido_routes import create_pedido_blueprint
from src.views.produto_routes import create_produto_blueprint
from src.views.relatorio_routes import create_relatorio_blueprint
from src.views.sistema_routes import create_sistema_blueprint
from src.views.usuario_routes import create_usuario_blueprint


def configure_logging(level):
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")


def create_app(settings=None):
    settings = settings or Settings.from_env()
    configure_logging(settings.LOG_LEVEL)

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=settings.SECRET_KEY,
        DATABASE_PATH=settings.DATABASE_PATH,
        ADMIN_TOKEN=settings.ADMIN_TOKEN,
    )
    CORS(app, origins=list(settings.CORS_ORIGINS))
    database.init_app(app)

    get_connection = database.get_connection
    produto_model = ProdutoModel(get_connection)
    usuario_model = UsuarioModel(get_connection)
    pedido_model = PedidoModel(get_connection)
    sistema_model = SistemaModel(get_connection)

    produto_controller = ProdutoController(produto_model)
    usuario_controller = UsuarioController(usuario_model)
    pedido_controller = PedidoController(pedido_model, produto_model, usuario_model, NotificationService())
    relatorio_controller = RelatorioController(pedido_model)
    sistema_controller = SistemaController(sistema_model, settings.APP_ENV, settings.ENABLE_ADMIN_QUERY)

    app.register_blueprint(create_produto_blueprint(produto_controller))
    app.register_blueprint(create_usuario_blueprint(usuario_controller))
    app.register_blueprint(create_pedido_blueprint(pedido_controller))
    app.register_blueprint(create_relatorio_blueprint(relatorio_controller))
    app.register_blueprint(create_sistema_blueprint(sistema_controller))
    register_error_handlers(app)
    return app
