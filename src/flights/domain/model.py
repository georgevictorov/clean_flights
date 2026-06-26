from dataclasses import dataclass
from enum import Enum
from typing import Iterable

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
            seats: Iterable[Seat],
            flight_status: FlightStatus = FlightStatus.OPEN,
            version_number: int = 1,
    ):
        self.flight_id = flight_id
        self._seats = {seat.seat_id: seat for seat in seats}
        self._flight_status = flight_status
        self.version_number = version_number

    @classmethod
    def create_new(cls, flight_id: str, seat_ids: list[str]) -> "Flight":
        seats = [Seat(seat_id) for seat_id in seat_ids]
        return cls(flight_id=flight_id, seats=seats)

    @property
    def flight_status(self) -> FlightStatus:
        return self._flight_status

    @property
    def seats(self) -> Iterable[Seat]:
        return self._seats.values()

    @property
    def persistence_state(self):

        return (
            self.flight_status,
            self.version_number,
            tuple(
                (
                    seat.seat_id,
                    seat.passenger_id,
                )
                for seat in self._seats.values()
            ),
        )

    def close_registration(self):
        if self._flight_status == FlightStatus.DEPARTED:
            raise errors.FlightDeparted()
        self._flight_status = FlightStatus.CLOSED

    def depart(self):
        self._flight_status = FlightStatus.DEPARTED

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
        seat = self._seats.get(seat_id)

        if seat is None:
            raise errors.SeatDoesNotExist(
                "seat does not exist"
            )

        return seat

    def _has_passenger(self, passenger_id: str) -> bool:
        return any(
            seat.passenger_id == passenger_id
            for seat in self._seats.values()
        )

    def _find_passenger_seat(self, passenger_id: str) -> Seat | None:
        return next(
            (
                seat
                for seat in self._seats.values()
                if seat.passenger_id == passenger_id
            ),
            None,
        )

    def __eq__(self, other):
        if not isinstance(other, Flight):
            return False
        return self.flight_id == other.flight_id

    def __hash__(self):
        return hash(self.flight_id)
