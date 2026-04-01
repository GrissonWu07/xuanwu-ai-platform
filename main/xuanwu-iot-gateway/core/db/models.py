from __future__ import annotations

from sqlalchemy import JSON, Column, DateTime, MetaData, String, func
from sqlalchemy.orm import DeclarativeMeta, declarative_base

_MODEL_CACHE: dict[str, tuple[DeclarativeMeta, type]] = {}


def create_models_for_schema(schema: str | None) -> tuple[DeclarativeMeta, type]:
    cache_key = schema or "__default__"
    cached = _MODEL_CACHE.get(cache_key)
    if cached is not None:
        return cached

    metadata = MetaData(schema=schema)
    base = declarative_base(metadata=metadata)

    class DeviceStateRecord(base):
        __tablename__ = "device_state"

        device_id = Column(String(255), primary_key=True)
        payload = Column(JSON, nullable=False)
        created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
        updated_at = Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        )

    _MODEL_CACHE[cache_key] = (base, DeviceStateRecord)
    return base, DeviceStateRecord
