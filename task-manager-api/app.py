"""Composition root: cria a app, carrega config, injeta dependências e registra rotas."""
import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Settings
from controllers.category_controller import CategoryController
from controllers.report_controller import ReportController
from controllers.task_controller import TaskController
from controllers.user_controller import UserController
from database import db
from middlewares.auth import Auth
from middlewares.error_handler import register_error_handlers
from models import User
from routes.category_routes import create_category_blueprint
from routes.main_routes import create_main_blueprint
from routes.report_routes import create_report_blueprint
from routes.task_routes import create_task_blueprint
from routes.user_routes import create_user_blueprint
from services.notification_service import NotificationService


def create_app(settings=None):
    settings = settings or Settings()
    logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=settings.SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=settings.DATABASE_URL,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    CORS(app, origins=settings.CORS_ORIGINS)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    notifier = NotificationService(settings)
    auth = Auth(settings.SECRET_KEY, settings.TOKEN_MAX_AGE_SECONDS, User.get_by_id)

    task_controller = TaskController(db.session, notifier)
    user_controller = UserController(db.session)
    category_controller = CategoryController(db.session)
    report_controller = ReportController()

    app.register_blueprint(create_main_blueprint())
    app.register_blueprint(create_task_blueprint(task_controller))
    app.register_blueprint(create_user_blueprint(user_controller, auth))
    app.register_blueprint(create_report_blueprint(report_controller))
    app.register_blueprint(create_category_blueprint(category_controller))

    register_error_handlers(app, db.session)
    return app


if __name__ == '__main__':
    app_settings = Settings()
    create_app(app_settings).run(host=app_settings.HOST, port=app_settings.PORT, debug=app_settings.DEBUG)
