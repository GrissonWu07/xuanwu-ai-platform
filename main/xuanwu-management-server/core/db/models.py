from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


def _schema_metadata(schema: str) -> MetaData:
    return MetaData(schema=schema)


class Base(DeclarativeBase):
    metadata = MetaData()


def create_base_for_schema(schema: str) -> type[DeclarativeBase]:
    class SchemaBase(DeclarativeBase):
        metadata = _schema_metadata(schema)

    return SchemaBase
