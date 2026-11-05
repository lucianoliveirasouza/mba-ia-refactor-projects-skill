"""Entry point: `python app.py`."""
import logging

from src.app import create_app
from src.config import Settings

settings = Settings.from_env()
app = create_app(settings)

if __name__ == "__main__":
    logging.getLogger(__name__).info("Servidor iniciado em http://%s:%s", settings.HOST, settings.PORT)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
