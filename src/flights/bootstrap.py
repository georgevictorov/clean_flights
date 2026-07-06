from psycopg_pool import ConnectionPool

from flights.config import get_postgres_uri
from flights.infrastructure.uow.postgres.postgres_uow import PostgresUnitOfWork
from flights.service_layer.service import FlightService


class Container:
    def __init__(self):
        self.pool = ConnectionPool(
            conninfo=get_postgres_uri(),
            min_size=1,
            max_size=4,
        )

        self.service = FlightService(
            PostgresUnitOfWork(self.pool)
        )

    def close(self):
        self.pool.close()
