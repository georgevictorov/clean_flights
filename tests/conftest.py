import pytest
from psycopg_pool import ConnectionPool

from flights.config import get_postgres_uri


@pytest.fixture(scope="session")
def db_pool():
    db_uri = get_postgres_uri()
    with ConnectionPool(
            conninfo=db_uri,
            min_size=1,
            max_size=4,
    ) as pool:
        yield pool


@pytest.fixture
def db_connection(db_pool):
    with db_pool.connection() as conn:
        yield conn


@pytest.fixture
def clean_db(db_pool):
    with db_pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("truncate table flights, seats restart identity cascade")
        conn.commit()

    yield
