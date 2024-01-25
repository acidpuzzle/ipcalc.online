from pathlib import Path
from flask import Flask
from config import Configuration


version = "0.2"

ROOT_DIR = Path(__file__).parent


def get_app():
    app = Flask(__name__)
    app.config.from_object(Configuration)
    setattr(app, "version", version)
    return app


application = get_app()
