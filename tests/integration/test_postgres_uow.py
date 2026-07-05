import threading

import pytest

from flights.domain.errors import ConcurrencyError
from flights.domain.model import Flight
from flights.infrastructure.uow.postgres.postgres_uow import PostgresUnitOfWork


def get_flight_id_from_db(flight_id, db_connection):
    with db_connection.cursor() as cur:
        cur.execute(
            """
            select
                flight_id
            from flights
            where flight_id = %s
            """,
            (flight_id,),
        )
        return cur.fetchone()


def test_add_flight(db_pool, db_connection, clean_db):
    with PostgresUnitOfWork(db_pool) as uow:
        flight = Flight.create_new(
            flight_id="su-104",
            seat_ids=["A1", "A2", "A3", "A4"],
        )
        uow.flights.add(flight)
        uow.commit()

    row = get_flight_id_from_db("su-104", db_connection)

    assert row is not None
    assert row[0] == "su-104"


def test_rollback_discards_new_flight(db_pool, db_connection, clean_db):
    with PostgresUnitOfWork(db_pool) as uow:
        flight = Flight.create_new(
            flight_id="su-104",
            seat_ids=["A1", "A2"],
        )
        uow.flights.add(flight)

    row = get_flight_id_from_db("su-104", db_connection)

    assert row is None


def test_get_returns_same_instance(db_pool, clean_db):
    flight = Flight.create_new(
        flight_id="su-104",
        seat_ids=["A1", "A2"],
    )

    with PostgresUnitOfWork(db_pool) as uow:
        uow.flights.add(flight)
        uow.commit()

    with PostgresUnitOfWork(db_pool) as uow:
        f1 = uow.flights.get("su-104")
        f2 = uow.flights.get("su-104")

        assert f1 is f2


def test_commit_updates_existing_flight(db_pool, db_connection, clean_db):
    flight = Flight.create_new(
        flight_id="su-104",
        seat_ids=["A1", "A2"],
    )

    with PostgresUnitOfWork(db_pool) as uow:
        uow.flights.add(flight)
        uow.commit()

    with PostgresUnitOfWork(db_pool) as uow:
        flight = uow.flights.get("su-104")
        flight.reserve("passenger-1", "A1")

        uow.commit()

    with db_connection.cursor() as cur:
        cur.execute(
            """
            select passenger_id
            from seats
            where flight_id = %s
              and seat_id = %s
            """,
            ("su-104", "A1"),
        )
        row = cur.fetchone()

    assert row[0] == "passenger-1"


def test_commit_without_changes(db_pool, db_connection, clean_db):
    flight = Flight.create_new(
        flight_id="su-104",
        seat_ids=["A1", "A2"],
    )

    with PostgresUnitOfWork(db_pool) as uow:
        uow.flights.add(flight)
        uow.commit()

    with PostgresUnitOfWork(db_pool) as uow:
        uow.flights.get("su-104")
        uow.commit()

    with db_connection.cursor() as cur:
        cur.execute(
            """
            select version
            from flights
            where flight_id = %s
            """,
            ("su-104",),
        )
        version = cur.fetchone()[0]

    assert version == 1


def test_rollback_discards_changes(db_pool, db_connection, clean_db):
    flight = Flight.create_new(
        flight_id="su-104",
        seat_ids=["A1", "A2"],
    )

    with PostgresUnitOfWork(db_pool) as uow:
        uow.flights.add(flight)
        uow.commit()

    with PostgresUnitOfWork(db_pool) as uow:
        flight = uow.flights.get("su-104")
        flight.reserve("passenger-1", "A1")

    with db_connection.cursor() as cur:
        cur.execute(
            """
            select passenger_id
            from seats
            where flight_id = %s
              and seat_id = %s
            """,
            ("su-104", "A1"),
        )
        row = cur.fetchone()

    assert row[0] is None


def test_get_returns_none_for_unknown_flight(db_pool, clean_db):
    with PostgresUnitOfWork(db_pool) as uow:
        flight = uow.flights.get("unknown")

    assert flight is None


def test_optimistic_locking(db_pool, clean_db):
    flight = Flight.create_new(
        flight_id="su-104",
        seat_ids=["A1", "A2"],
    )

    with PostgresUnitOfWork(db_pool) as uow:
        uow.flights.add(flight)
        uow.commit()

    uow1 = PostgresUnitOfWork(db_pool)
    uow2 = PostgresUnitOfWork(db_pool)

    with uow1:  # noqa
        with uow2:
            flight1 = uow1.flights.get("su-104")
            flight2 = uow2.flights.get("su-104")

            flight1.reserve("p1", "A1")
            uow1.commit()

            flight2.reserve("p2", "A2")

            with pytest.raises(ConcurrencyError):
                uow2.commit()


def test_optimistic_locking_threads(db_pool, clean_db):
    with PostgresUnitOfWork(db_pool) as uow:
        uow.flights.add(
            Flight.create_new(
                flight_id="su-104",
                seat_ids=["A1", "A2"],
            )
        )
        uow.commit()

    barrier = threading.Barrier(2)
    errors = []

    def worker(passenger_id, seat_id):
        try:
            with PostgresUnitOfWork(db_pool) as postgres_uow:
                flight = postgres_uow.flights.get("su-104")

                flight.reserve(passenger_id, seat_id)

                barrier.wait()

                postgres_uow.commit()

            errors.append("ok")

        except ConcurrencyError:
            errors.append("concurrency")

    t1 = threading.Thread(target=worker, args=("p2", "A1"))
    t2 = threading.Thread(target=worker, args=("p3", "A2"))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    assert errors.count("ok") == 1
    assert errors.count("concurrency") == 1
