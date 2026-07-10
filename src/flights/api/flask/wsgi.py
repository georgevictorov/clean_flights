from flights.api.flask.app import create_app
from flights.bootstrap import Container
from flights.logger import configure_logging

configure_logging()

application = create_app(Container)
