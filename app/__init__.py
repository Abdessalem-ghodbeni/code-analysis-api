from flask import Flask
from .routes import init_routes


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config/settings.py")
    init_routes(app)
    return app
