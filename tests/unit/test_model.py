import pytest

from flights.domain import errors, model


def create_flight():
    return model.Flight(
        flight_id="su-104",
        version_number=1,
        seats={"A1", "A2", "A3", "A4", "A5", "A6", "A7"},
        reservations={}
    )


def test_reserve_success_one():
    flight = create_flight()

    passenger_id = "p1"
    seat_id = "A2"

    flight.reserve(passenger_id, seat_id)

    assert "A2" in flight.reservations


def test_reserve_success_two():
    flight = create_flight()

    passenger_id = "p2"
    seat_id = "A3"
    passenger_id2 = "p3"
    seat_id2 = "A4"

    flight.reserve(passenger_id, seat_id)
    flight.reserve(passenger_id2, seat_id2)

    assert "A3" in flight.reservations
    assert "A4" in flight.reservations


def test_reserve_failure_status_closed():
    flight = create_flight()
    flight.flight_status = model.FlightStatus.CLOSED

    passenger_id = "p1"
    seat_id = "A2"

    with pytest.raises(errors.FlightClosed):
        flight.reserve(passenger_id, seat_id)


def test_reserve_failure_seat_does_not_exist():
    flight = create_flight()

    passenger_id = "p1"
    seat_id = "B2"

    with pytest.raises(errors.SeatDoesNotExist):
        flight.reserve(passenger_id, seat_id)


def test_reserve_failure_seat_already_reserved():
    flight = create_flight()

    passenger_id = "p1"
    seat_id = "A2"

    flight.reserve(passenger_id, seat_id)

    with pytest.raises(errors.SeatAlreadyReserved):
        flight.reserve(passenger_id, seat_id)


def test_reserve_failure_passenger_already_registered():
    flight = create_flight()

    passenger_id = "p1"
    seat_id = "A2"

    flight.reserve(passenger_id, seat_id)

    passenger_id2 = "p1"
    seat_id2 = "A3"

    with pytest.raises(errors.PassengerAlreadyRegistered):
        flight.reserve(passenger_id2, seat_id2)


def test_cancel_success():
    flight = create_flight()

    passenger_id = "p1"
    seat_id = "A2"

    flight.reserve(passenger_id, seat_id)

    assert "A2" in flight.reservations

    flight.cancel(passenger_id, seat_id)
    flight.cancel(passenger_id, seat_id)
    flight.cancel(passenger_id, seat_id)

    assert "A2" not in flight.reservations


def test_cancel_failure_flight_departed():
    flight = create_flight()

    passenger_id = "p1"
    seat_id = "A2"

    flight.reserve(passenger_id=passenger_id, seat_id=seat_id)

    flight.flight_status = model.FlightStatus.DEPARTED

    with pytest.raises(errors.FlightDeparted):
        flight.cancel(passenger_id=passenger_id, seat_id=seat_id)


def test_cancel_failure_passenger_not_reservation_owner():
    flight = create_flight()

    passenger_id = "p1"
    seat_id = "A2"

    passenger_id2 = "p2"
    seat_id2 = "A2"

    flight.reserve(passenger_id=passenger_id, seat_id=seat_id)

    with pytest.raises(errors.NotReservationOwner):
        flight.cancel(passenger_id2, seat_id2)
