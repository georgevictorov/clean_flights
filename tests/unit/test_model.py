import pytest

from flights.domain import errors, model


def create_flight():
    return model.Flight.create_new(
        flight_id="su-104",
        seat_ids=["A1", "A2", "A3", "A4"],
    )


# RESERVE

def test_reserve_success():
    flight = create_flight()

    flight.reserve("p1", "A2")

    assert flight._get_seat("A2").passenger_id == "p1"


def test_reserve_multiple_success():
    flight = create_flight()

    flight.reserve("p1", "A2")
    flight.reserve("p2", "A3")

    assert flight._get_seat("A2").passenger_id == "p1"
    assert flight._get_seat("A3").passenger_id == "p2"


def test_reserve_failure_flight_closed():
    flight = create_flight()
    flight.close_registration()

    with pytest.raises(errors.FlightClosed):
        flight.reserve("p1", "A2")


def test_reserve_failure_seat_does_not_exist():
    flight = create_flight()

    with pytest.raises(errors.SeatDoesNotExist):
        flight.reserve("p1", "B2")


def test_reserve_failure_passenger_already_registered():
    flight = create_flight()

    flight.reserve("p1", "A2")

    with pytest.raises(errors.PassengerAlreadyRegistered):
        flight.reserve("p1", "A3")


def test_reserve_failure_seat_already_reserved_by_other():
    flight = create_flight()

    flight.reserve("p1", "A2")

    with pytest.raises(errors.SeatAlreadyReserved):
        flight.reserve("p2", "A2")


# CANCEL

def test_cancel_success():
    flight = create_flight()

    flight.reserve("p1", "A2")
    flight.cancel("p1")

    assert flight._get_seat("A2").passenger_id is None
    assert not flight._has_passenger("p1")


def test_cancel_idempotent():
    flight = create_flight()

    flight.reserve("p1", "A2")

    flight.cancel("p1")
    flight.cancel("p1")
    flight.cancel("p1")

    assert flight._get_seat("A2").passenger_id is None


def test_cancel_unknown_passenger_is_noop():
    flight = create_flight()

    flight.reserve("p1", "A2")

    flight.cancel("p2")

    assert flight._get_seat("A2").passenger_id == "p1"


def test_cancel_failure_flight_departed():
    flight = create_flight()

    flight.reserve("p1", "A2")
    flight.depart()

    with pytest.raises(errors.FlightDeparted):
        flight.cancel("p1")


# INVARIANTS / EDGE CASES

def test_reserve_after_cancel_same_seat():
    flight = create_flight()

    flight.reserve("p1", "A2")
    flight.cancel("p1")

    flight.reserve("p2", "A2")

    assert flight._get_seat("A2").passenger_id == "p2"


def test_flight_equality():
    f1 = create_flight()
    f2 = create_flight()

    assert f1 == f2

    f3 = model.Flight.create_new(
        flight_id="different",
        seat_ids=["A1", "A2", "A3", "A4"],
    )

    assert f1 != f3
