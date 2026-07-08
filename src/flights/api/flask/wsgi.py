from flights.api.flask.app import create_app
from flights.bootstrap import Container

application = create_app(Container)
