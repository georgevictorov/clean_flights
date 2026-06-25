from dataclasses import dataclass
from enum import Enum

from flights.domain import errors


class FlightStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    DEPARTED = "departed"


@dataclass
class Seat:
    seat_id: str
    passenger_id: str | None = None

    @property
    def is_reserved(self) -> bool:
        return self.passenger_id is not None

    def assign(self, passenger_id: str):
        self.passenger_id = passenger_id

    def clear(self):
        self.passenger_id = None


class Flight:
    def __init__(
            self,
            flight_id: str,
            seats: dict[str, Seat],
            flight_status: FlightStatus = FlightStatus.OPEN,
            version_number: int = 1,
    ):
        self.flight_id = flight_id
        self.seats = seats
        self.flight_status = flight_status
        self.version_number = version_number

    def reserve(self, passenger_id: str, seat_id: str):
        if self.flight_status != FlightStatus.OPEN:
            raise errors.FlightClosed()

        if self._has_passenger(passenger_id):
            raise errors.PassengerAlreadyRegistered('passenger already registered')

        seat = self._get_seat(seat_id)

        if seat.is_reserved:
            raise errors.SeatAlreadyReserved('seat already reserved')

        seat.assign(passenger_id)

    def cancel(self, passenger_id: str):
        if self.flight_status == FlightStatus.DEPARTED:
            raise errors.FlightDeparted('flight departed')

        seat = self._find_passenger_seat(passenger_id)

        if seat is None:
            return

        seat.clear()

    def _get_seat(self, seat_id: str) -> Seat:
        seat = self.seats.get(seat_id)

        if seat is None:
            raise errors.SeatDoesNotExist(
                "seat does not exist"
            )

        return seat

    def _has_passenger(self, passenger_id: str) -> bool:
        return any(
            seat.passenger_id == passenger_id
            for seat in self.seats.values()
        )

    def _find_passenger_seat(self, passenger_id: str) -> Seat | None:
        return next(
            (
                seat
                for seat in self.seats.values()
                if seat.passenger_id == passenger_id
            ),
            None,
        )

    def __eq__(self, other):
        if not isinstance(other, Flight):
            return False
        return self.flight_id == other.flight_id
