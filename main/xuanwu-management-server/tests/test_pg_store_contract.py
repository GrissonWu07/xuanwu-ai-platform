from __future__ import annotations

import tempfile
from pathlib import Path


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


def test_pg_store_round_trips_user_device_and_schedule() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "control-plane.db"
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
            store.create_user({"user_id": "u1", "name": "User 1"})
            store.save_device("d1", {"device_id": "d1", "user_id": "u1"})
            store.save_schedule(
                "s1",
                {
                    "schedule_id": "s1",
                    "job_type": "device_command",
                    "executor_type": "iot_gateway",
                },
            )

            assert store.get_user("u1")["user_id"] == "u1"
            assert store.get_device("d1")["device_id"] == "d1"
            assert store.get_schedule("s1")["schedule_id"] == "s1"
        finally:
            store.close()
