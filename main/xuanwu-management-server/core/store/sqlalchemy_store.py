from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from core.db.bootstrap import ensure_schema_exists
from core.db.engine import create_db_engine
from core.db.models import create_models_for_schema
from core.store.local_store import LocalControlPlaneStore


class SQLAlchemyControlPlaneStore(LocalControlPlaneStore):
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.root_dir = Path("__pg_store__")
        self.engine: Engine = create_db_engine(config)
        schema = str(config.get("control-plane", {}).get("postgres", {}).get("schema") or "xw_mgmt").strip()
        self._schema = None if self.engine.dialect.name == "sqlite" else schema
        self._base, self._record_model = create_models_for_schema(self._schema)
        ensure_schema_exists(config, engine=self.engine)
        self._base.metadata.create_all(self.engine)
        self.session_factory: sessionmaker[Session] = sessionmaker(
            bind=self.engine,
            future=True,
            expire_on_commit=False,
        )

    @classmethod
    def from_config(cls, config: dict[str, Any], *, project_dir: str | Path | None = None):
        return cls(config)

    def _split_path(self, path: Path) -> tuple[str, str]:
        relative = path.relative_to(self.root_dir)
        collection = relative.parent.as_posix() or "__root__"
        return collection, relative.stem

    def close(self) -> None:
        self.engine.dispose()

    def _fetch_record(self, session: Session, collection: str, record_id: str):
        return session.get(self._record_model, {"collection": collection, "record_id": record_id})

    def _record_exists(self, path: Path) -> bool:
        collection, record_id = self._split_path(path)
        with self.session_factory() as session:
            return self._fetch_record(session, collection, record_id) is not None

    def _delete_path(self, path: Path) -> bool:
        collection, record_id = self._split_path(path)
        with self.session_factory.begin() as session:
            record = self._fetch_record(session, collection, record_id)
            if record is None:
                return False
            session.delete(record)
        return True

    def _read_yaml(self, path: Path, default: dict[str, Any] | None = None) -> dict[str, Any] | None:
        collection, record_id = self._split_path(path)
        with self.session_factory() as session:
            record = self._fetch_record(session, collection, record_id)
            if record is None:
                return deepcopy(default) if default is not None else None
            return deepcopy(record.payload)

    def _write_yaml(self, path: Path, payload: dict[str, Any]):
        collection, record_id = self._split_path(path)
        materialized = deepcopy(payload)
        with self.session_factory.begin() as session:
            record = self._fetch_record(session, collection, record_id)
            if record is None:
                record = self._record_model(
                    collection=collection,
                    record_id=record_id,
                    payload=materialized,
                )
                session.add(record)
            else:
                record.payload = materialized

    def _list_yaml_dir(self, path: Path) -> list[dict[str, Any]]:
        collection = path.relative_to(self.root_dir).as_posix() or "__root__"
        with self.session_factory() as session:
            records = session.scalars(
                select(self._record_model)
                .where(self._record_model.collection == collection)
                .order_by(self._record_model.record_id.asc())
            ).all()
        return [deepcopy(record.payload) for record in records]

    def delete_user(self, user_id: str) -> bool:
        return self._delete_path(self.root_dir / "users" / f"{user_id}.yaml")

    def delete_auth_session(self, session_token: str) -> bool:
        return self._delete_path(self.root_dir / "auth_sessions" / f"{session_token}.yaml")

    def delete_channel(self, channel_id: str) -> bool:
        return self._delete_path(self.root_dir / "channels" / f"{channel_id}.yaml")

    def get_active_device_agent_mapping(self, device_id: str) -> dict[str, Any] | None:
        items = self._list_yaml_dir(self.root_dir / "device_agent_mappings")
        for payload in items:
            if payload.get("device_id") != device_id:
                continue
            if payload.get("enabled", True) is False:
                continue
            return payload
        return None

    def _replace_user_device_mappings_for_device(self, user_id: str, device_id: str):
        with self.session_factory.begin() as session:
            records = session.scalars(
                select(self._record_model).where(self._record_model.collection == "user_device_mappings")
            ).all()
            for record in records:
                if str((record.payload or {}).get("device_id") or "").strip() == device_id:
                    session.delete(record)
        self._sync_user_device_mapping(user_id, device_id)
