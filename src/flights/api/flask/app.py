import atexit

from flask import Flask

from flights.api.flask.errors import register_error_handlers
from flights.api.flask.routes import register_routes


def create_app(container_factory):
    flask_app = Flask(__name__)
    container = container_factory()

    register_routes(flask_app, container.service)
    register_error_handlers(flask_app)

    atexit.register(container.close)

    return flask_app
