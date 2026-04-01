from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from core.db.engine import create_db_engine


def create_session_factory(config: dict) -> sessionmaker[Session]:
    engine = create_db_engine(config)
    return sessionmaker(bind=engine, future=True, expire_on_commit=False)
