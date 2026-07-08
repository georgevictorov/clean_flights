def test_create_flight(client, api_url, clean_db):
    response = client.post(
        f"{api_url}/create_flight",
        json={
            "flight_id": "SU-100",
            "seats": ["A1", "A2"],
        },
    )

    assert response.status_code == 201
    assert response.json() == {"msg": "ok"}


def test_create_flight_duplicate(client, api_url, clean_db):
    payload = {
        "flight_id": "SU-100",
        "seats": ["A1", "A2"],
    }

    response = client.post(
        f"{api_url}/create_flight",
        json=payload,
    )

    assert response.status_code == 201

    response = client.post(
        f"{api_url}/create_flight",
        json=payload,
    )

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
