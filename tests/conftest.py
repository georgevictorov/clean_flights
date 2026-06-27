import sqlite3
import pytest

from flights.infrastructure.repo.sqlite.schema import SCHEMA


@pytest.fixture
def sqlite_session_factory():
    db_uri = "file:memdb1?mode=memory&cache=shared"

    main_conn = sqlite3.connect(db_uri, uri=True)
    main_conn.executescript(SCHEMA)

    yield lambda: sqlite3.connect(db_uri, uri=True)

    main_conn.close()
