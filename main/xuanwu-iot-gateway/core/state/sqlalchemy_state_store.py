from __future__ import annotations

from copy import deepcopy

from sqlalchemy.orm import Session, sessionmaker

from core.db.bootstrap import ensure_schema_exists
from core.db.engine import create_db_engine
from core.db.models import create_models_for_schema


class SQLAlchemyStateStore:
    def __init__(self, config: dict):
        self.config = config
        self.engine = create_db_engine(config)
        schema = str(config.get("state", {}).get("postgres", {}).get("schema") or "xw_iot").strip()
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
    def from_config(cls, config: dict):
        return cls(config)

    def close(self) -> None:
        self.engine.dispose()

    def get_device_state(self, device_id: str) -> dict:
        with self.session_factory() as session:
            record = session.get(self._record_model, {"device_id": device_id})
            if record is None:
                return {"device_id": device_id, "status": "unknown"}
            return deepcopy(record.payload)

    def upsert_device_state(self, device_id: str, payload: dict) -> dict:
        state = self.get_device_state(device_id)
        if state.get("status") == "unknown" and len(state) == 2:
            state = {"device_id": device_id}
        state.update(deepcopy(payload))
        state["device_id"] = device_id
        with self.session_factory.begin() as session:
            record = session.get(self._record_model, {"device_id": device_id})
            if record is None:
                record = self._record_model(device_id=device_id, payload=state)
                session.add(record)
            else:
                record.payload = state
        return deepcopy(state)
