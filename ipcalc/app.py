from flask import Flask
from ipcalc.config import Configuration


application = Flask(__name__)
application.config.from_object(Configuration)
