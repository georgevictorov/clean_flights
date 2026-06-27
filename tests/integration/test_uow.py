from flights.domain.model import Flight
from flights.infrastructure.uow.sqlite.sqlite_uow import SqliteUnitOfWork


def get_flight_id_from_db(flight_id, sqlite_session_factory):
    with sqlite_session_factory() as db_conn:
        return db_conn.execute(
            """
            select
                flight_id
            from flights
            where
                flight_id = ? 
            """,
            [flight_id],
        ).fetchone()


def test_add_flight(sqlite_session_factory):
    uow = SqliteUnitOfWork(sqlite_session_factory)
    with uow:
        flight = Flight.create_new(
            flight_id="su-104",
            seat_ids=["A1", "A2", "A3", "A4"],
        )
        uow.flights.add(flight)
        uow.commit()

    row = get_flight_id_from_db("su-104", sqlite_session_factory)

    assert row is not None
    assert row[0] == "su-104"

