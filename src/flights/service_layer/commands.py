from dataclasses import dataclass


class Command:
    pass


@dataclass(frozen=True)
class CreateFlight(Command):
    flight_id: str
    seat_ids: list[str]


@dataclass(frozen=True)
class ReserveSeat(Command):
    flight_id: str
    passenger_id: str
    seat_id: str


@dataclass(frozen=True)
class CancelReservation(Command):
    flight_id: str
    passenger_id: str
