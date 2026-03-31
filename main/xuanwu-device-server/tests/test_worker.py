import asyncio
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import types


SERVICE_ROOT = Path(__file__).resolve().parents[1]
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))


fake_logger_module = types.ModuleType("config.logger")
fake_logger_module.setup_logging = lambda: None
sys.modules.setdefault("config.logger", fake_logger_module)


def _load_worker_module():
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-device-server" / "core" / "worker.py"
    service_root = module_path.parents[1]

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for module_name in list(sys.modules):
        if module_name == "config" or module_name.startswith("config."):
            sys.modules.pop(module_name, None)
        if module_name == "core" or module_name.startswith("core."):
            sys.modules.pop(module_name, None)
    sys.modules.setdefault("config.logger", fake_logger_module)

    spec = spec_from_file_location("xuanwu_device_worker", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _FakeCacheManager:
    def __init__(self):
        self.cleared = []

    def clear(self, cache_type):
        self.cleared.append(cache_type)


class _FakeManagementClient:
    def __init__(self):
        self.completed = []
        self.failed = []

    async def complete_job_run(self, job_run_id: str, payload: dict):
        self.completed.append((job_run_id, payload))

    async def fail_job_run(self, job_run_id: str, payload: dict):
        self.failed.append((job_run_id, payload))


def test_device_worker_refreshes_runtime_config_and_clears_cache():
    module = _load_worker_module()
    fake_cache_manager = _FakeCacheManager()
    fake_client = _FakeManagementClient()
    module.cache_manager = fake_cache_manager
    module.CacheType = types.SimpleNamespace(CONFIG="config")
    module.load_config = lambda: {
        "selected_module": {"LLM": "OpenAI"},
        "server": {"port": 8000},
    }

    result = asyncio.run(
        module.run_device_job(
            {"management_client": fake_client},
            {
                "job_run_id": "run-device-001",
                "job_type": "runtime_config_refresh",
                "payload": {"reason": "operator_request"},
            },
        )
    )

    assert result == {
        "status": "completed",
        "job_type": "runtime_config_refresh",
        "result": {
            "selected_module": {"LLM": "OpenAI"},
            "server": {"port": 8000},
        },
    }
    assert fake_cache_manager.cleared == ["config"]
    assert fake_client.completed == [("run-device-001", result)]
    assert fake_client.failed == []


def test_device_worker_unregisters_runtime_session():
    module = _load_worker_module()
    fake_client = _FakeManagementClient()

    class DummyConn:
        pass

    module.runtime_session_registry.register(
        "runtime-session-001",
        device_id="esp32-001",
        client_id="client-001",
        xuanwu_session_key="xuanwu-session-001",
        conn=DummyConn(),
    )

    result = asyncio.run(
        module.run_device_job(
            {"management_client": fake_client},
            {
                "job_run_id": "run-device-002",
                "job_type": "runtime_session_unregister",
                "payload": {"runtime_session_id": "runtime-session-001"},
            },
        )
    )

    assert result["status"] == "completed"
    assert (
        module.runtime_session_registry.get_by_runtime_session("runtime-session-001")
        is None
    )
    assert fake_client.completed == [("run-device-002", result)]
