from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def build_postgres_url(config: dict) -> str:
    postgres = config["control-plane"]["postgres"]
    return (
        f"postgresql+psycopg://{postgres['user']}:{postgres['password']}"
        f"@{postgres['host']}:{postgres['port']}/{postgres['database']}"
    )


def create_db_engine(config: dict) -> Engine:
    return create_engine(build_postgres_url(config), future=True)
