from pathlib import Path
import logging
import click
from flask import Flask
from config import Configuration
from logging.config import dictConfig


version = "0.2"

ROOT_DIR = Path(__file__).parent
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "debug.log"


class RemoveColorFilter(logging.Filter):
    def filter(self, record):
        if record and record.msg and isinstance(record.msg, str):
            record.msg = click.unstyle(record.msg)
        return True


LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '{asctime} @{levelname} {name}.{funcName} => {message}',
            "style": "{",
        }
    },
    "filters": {
        "no_colors": {
            "()": "ip_calc_app.RemoveColorFilter",
        },
    },

    'handlers': {
        'wsgi': {
            "level": "INFO",
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default',
            "filters": ["no_colors"],
        },
        "file": {
            'class': 'logging.handlers.RotatingFileHandler',
            "level": "DEBUG",
            "filename": LOG_FILE.as_posix(),
            "mode": "a",
            'maxBytes': 10485760,
            'backupCount': 5,
            "encoding": "UTF-8",
            "formatter": "default",
            "filters": ["no_colors"],
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file'],
        "propagate": True,
    },
    "werkzeug": {
        'level': 'INFO',
        'handlers': ['wsgi', 'file'],
        "propagate": True,

    }
}


def get_app():
    dictConfig(LOG_CONFIG)
    app = Flask(__name__)
    app.config.from_object(Configuration)
    setattr(app, "version", version)
    return app


application = get_app()

