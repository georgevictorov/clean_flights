import os


def get_postgres_uri() -> str:
    return os.getenv("DATABASE_URL", "postgresql://postgres:abc123@localhost:5432/flights")
