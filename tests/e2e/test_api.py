def create_flight(client, api_url, flight_id="SU-100", seats=None):
    if seats is None:
        seats = ["A1", "A2"]

    return client.post(
        f"{api_url}/create_flight",
        json={
            "flight_id": flight_id,
            "seats": seats,
        },
    )


def reserve_seat(client, api_url, flight_id="SU-100", passenger_id="P1", seat_id="A1"):
    return client.post(
        f"{api_url}/reserve_seat",
        json={
            "flight_id": flight_id,
            "passenger_id": passenger_id,
            "seat_id": seat_id,
        },
    )


def cancel_registration(client, api_url, flight_id="SU-100", passenger_id="P1"):
    return client.post(
        f"{api_url}/cancel_reservation",
        json={
            "flight_id": flight_id,
            "passenger_id": passenger_id,
        }
    )


def test_create_flight(client, api_url, clean_db):
    response = create_flight(client, api_url)

    assert response.status_code == 201
    assert response.json() == {"msg": "ok"}


def test_create_flight_duplicate(client, api_url, clean_db):
    response = create_flight(client, api_url)

    assert response.status_code == 201

    response = create_flight(client, api_url)

    assert response.status_code == 409
    assert response.json() == {"msg": "flight already exists"}


def test_create_flight_missing_fields(client, api_url, clean_db):
    payload = {
        "seats": ["A1", "A2"],
    }

    response = client.post(
        f"{api_url}/create_flight",
        json=payload,
    )

    assert response.status_code == 400
    assert response.json() == {"msg": "missing required field: flight_id"}

    payload = {
        "flight_id": "SU-100",
    }

    response = client.post(
        f"{api_url}/create_flight",
        json=payload,
    )

    assert response.status_code == 400
    assert response.json() == {"msg": "missing required field: seats"}


def test_reserve_seat(client, api_url, clean_db):
    response = create_flight(client, api_url)

    assert response.status_code == 201

    response = reserve_seat(client, api_url)

    assert response.status_code == 204


def test_reserve_seat_flight_not_found(client, api_url, clean_db):
    response = reserve_seat(client, api_url)

    assert response.status_code == 404
    assert response.json() == {"msg": "flight not found"}


def test_reserve_seat_seat_does_not_exist(client, api_url, clean_db):
    response = create_flight(client, api_url)

    assert response.status_code == 201

    response = reserve_seat(client, api_url, seat_id="B1")

    assert response.status_code == 404
    assert response.json() == {"msg": "seat does not exist"}


def test_reserve_seat_passenger_already_registered(client, api_url, clean_db):
    response = create_flight(client, api_url)

    assert response.status_code == 201

    response = reserve_seat(client, api_url)

    assert response.status_code == 204

    response = reserve_seat(client, api_url, passenger_id="P1", seat_id="A2")

    assert response.status_code == 409
    assert response.json() == {"msg": "passenger already registered"}


def test_reserve_seat_seat_already_reserved(client, api_url, clean_db):
    response = create_flight(client, api_url)

    assert response.status_code == 201

    response = reserve_seat(client, api_url)

    assert response.status_code == 204

    response = reserve_seat(client, api_url, passenger_id="P2")

    assert response.status_code == 409
    assert response.json() == {"msg": "seat already reserved"}


def test_cancel_reservation(client, api_url, clean_db):
    response = create_flight(client, api_url)

    assert response.status_code == 201

    response = reserve_seat(client, api_url)

    assert response.status_code == 204

    response = cancel_registration(client, api_url)

    assert response.status_code == 204


def test_cancel_reservation_flight_not_found(client, api_url, clean_db):
    response = cancel_registration(client, api_url)

    assert response.status_code == 404
    assert response.json() == {"msg": "flight not found"}
