from __future__ import annotations

from sqlalchemy import text

from core.db.engine import create_db_engine


def ensure_schema_exists(config: dict) -> None:
    schema = config["control-plane"]["postgres"]["schema"]
    engine = create_db_engine(config)
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
