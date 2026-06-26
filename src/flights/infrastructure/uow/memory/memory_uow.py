from flights.infrastructure.repo.memory.memory_repository import \
    InMemoryRepository
from flights.service_layer.repository import AbstractRepository
from flights.service_layer.uow import AbstractUnitOfWork


class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.flights: AbstractRepository = InMemoryRepository()
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
