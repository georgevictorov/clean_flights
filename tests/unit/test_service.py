import pytest

from flights.domain.commands import CreateFlight, ReserveSeat
from flights.domain.errors import FlightAlreadyExists
from flights.infrastructure.uow.memory.memory_uow import InMemoryUnitOfWork
from flights.infrastructure.repo.memory.memory_repository import InMemoryRepository
from flights.service_layer.service import FlightService


def create_unit_of_work():
    uow = InMemoryUnitOfWork(InMemoryRepository())
    return uow


def create_command_create_flight():
    cmd = CreateFlight(
        flight_id="SU-901",
        seat_ids=["A1", "A2", "A3"],
    )
    return cmd


def create_command_reserve_seat():
    cmd = ReserveSeat(
        flight_id="SU-901",
        passenger_id="p01",
        seat_id="A1"
    )
    return cmd


def test_create_flight_success():
    uow = create_unit_of_work()
    service = FlightService(uow)
    cmd = create_command_create_flight()
    service.create_flight(cmd)

    assert uow.flights.get(flight_id="SU-901").flight_id == cmd.flight_id


def test_create_flight_already_exists_failure():
    uow = create_unit_of_work()
    service = FlightService(uow)
    cmd = create_command_create_flight()
    service.create_flight(cmd)

    with pytest.raises(FlightAlreadyExists):
        service.create_flight(cmd)


def test_reserve_seat_success():
    uow = create_unit_of_work()
    service = FlightService(uow)

    cmd = create_command_create_flight()
    service.create_flight(cmd)

    cmd = create_command_reserve_seat()

    service.reserve_seat(cmd)

    flight = uow.flights.get(flight_id="SU-901")
    seat = next(s for s in flight.seats if s.seat_id == cmd.seat_id)

    assert seat.passenger_id == cmd.passenger_id
    assert seat.is_reserved
