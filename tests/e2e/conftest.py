import time

import pytest
import requests

BASE_URL = "http://api"
RETRIES = 5


@pytest.fixture(scope="session", autouse=True)
def wait_for_api():
    for _ in range(RETRIES):
        try:
            response = requests.get(BASE_URL)
            assert response.status_code == 200
            assert response.json() == {"msg": "hey"}
            return
        except requests.ConnectionError:
            time.sleep(1)

    pytest.fail("API did not start")


@pytest.fixture
def client():
    with requests.Session() as session:
        yield session


@pytest.fixture
def api_url():
    return BASE_URL
