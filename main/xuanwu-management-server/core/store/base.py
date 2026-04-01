from __future__ import annotations

from typing import Protocol


class ControlPlaneStore(Protocol):
    def load_server_profile(self) -> dict: ...

    def save_server_profile(self, payload: dict) -> dict: ...


def create_control_plane_store(config: dict):
    backend = str(config.get("control-plane", {}).get("backend") or "local").strip().lower()
    if backend == "postgres":
        from core.store.sqlalchemy_store import SQLAlchemyControlPlaneStore

        return SQLAlchemyControlPlaneStore.from_config(config)

    from core.store.local_store import LocalControlPlaneStore

    return LocalControlPlaneStore.from_config(config)
