from flights.infrastructure.repo.sqlite.sqlite_repository import \
    SqliteRepository
from flights.service_layer.uow import AbstractUnitOfWork


class SqliteUnitOfWork(AbstractUnitOfWork):

    def __init__(self, connection_factory):
        self._connection_factory = connection_factory

    def __enter__(self):
        self.conn = self._connection_factory()

        self.flights = SqliteRepository(self.conn)

        return super().__enter__()

    def commit(self):
        self.flights.flush()  # noqa
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def __exit__(self, *args):
        super().__exit__(*args)

        self.conn.close()
