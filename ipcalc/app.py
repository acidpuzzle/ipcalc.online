from flask import Flask
from config import Configuration


application = Flask(__name__)
application.config.from_object(Configuration)
