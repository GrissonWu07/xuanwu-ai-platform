from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine

from core.db.engine import create_db_engine


def ensure_schema_exists(config: dict, *, engine: Engine | None = None) -> None:
    schema = config["state"]["postgres"]["schema"]
    engine = engine or create_db_engine(config)
    if engine.dialect.name == "sqlite":
        return
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
