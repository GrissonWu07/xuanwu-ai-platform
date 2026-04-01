from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def build_database_url(config: dict) -> str:
    postgres = config["state"]["postgres"]
    direct_url = str(postgres.get("url") or "").strip()
    if direct_url:
        return direct_url
    return (
        f"postgresql+psycopg://{postgres['user']}:{postgres['password']}"
        f"@{postgres['host']}:{postgres['port']}/{postgres['database']}"
    )


def create_db_engine(config: dict) -> Engine:
    return create_engine(build_database_url(config), future=True, pool_pre_ping=True)
