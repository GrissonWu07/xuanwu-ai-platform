from __future__ import annotations

import tempfile
from pathlib import Path

import yaml


SERVICE_ROOT = Path(__file__).resolve().parents[1]
import sys

if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))
for module_name in list(sys.modules):
    if module_name == "config" or module_name.startswith("config."):
        sys.modules.pop(module_name, None)
    if module_name == "core" or module_name.startswith("core."):
        sys.modules.pop(module_name, None)

from core.store.sqlalchemy_store import SQLAlchemyControlPlaneStore
from scripts.import_yaml_control_plane import import_yaml_control_plane


def _write_yaml(root: Path, relative_path: str, payload: dict) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def test_import_yaml_control_plane_imports_devices_and_users() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        source_root = temp_root / "source"
        db_path = temp_root / "control-plane.db"
        _write_yaml(source_root, "users/u1.yaml", {"user_id": "u1", "name": "User 1"})
        _write_yaml(source_root, "devices/d1.yaml", {"device_id": "d1", "user_id": "u1"})

        config = {
            "control-plane": {
                "backend": "postgres",
                "postgres": {
                    "url": f"sqlite+pysqlite:///{db_path.as_posix()}",
                    "schema": "xw_mgmt",
                },
            }
        }

        store = SQLAlchemyControlPlaneStore.from_config(config)
        try:
            import_yaml_control_plane(source_root, store)
            assert store.get_user("u1")["user_id"] == "u1"
            assert store.get_device("d1")["device_id"] == "d1"
        finally:
            store.close()
