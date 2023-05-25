from flask import Flask
from config import Configuration

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


application = Flask(__name__)
application.config.from_object(Configuration)
