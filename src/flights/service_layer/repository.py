from typing import Protocol

from flights.domain.model import Flight


class AbstractRepository(Protocol):
    def get(self, flight_id: str) -> Flight | None:
        ...

    def add(self, flight: Flight):
        ...
