import asyncio
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def _load_worker_module():
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-gateway" / "core" / "worker.py"
    service_root = module_path.parents[1]

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for module_name in list(sys.modules):
        if module_name == "config" or module_name.startswith("config."):
            sys.modules.pop(module_name, None)
        if module_name == "core" or module_name.startswith("core."):
            sys.modules.pop(module_name, None)

    spec = spec_from_file_location("xuanwu_gateway_worker", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _FakeManagementClient:
    def __init__(self):
        self.completed = []
        self.failed = []

    async def complete_job_run(self, job_run_id: str, payload: dict):
        self.completed.append((job_run_id, payload))

    async def fail_job_run(self, job_run_id: str, payload: dict):
        self.failed.append((job_run_id, payload))


def test_gateway_worker_dispatches_supported_adapter_and_reports_completion():
    module = _load_worker_module()
    client = _FakeManagementClient()
    ctx = {"management_client": client}
    job_message = {
        "job_run_id": "run-gateway-001",
        "schedule_id": "sched-gateway-001",
        "job_type": "device_command",
        "executor_type": "gateway",
        "scheduled_for": "2026-03-31T10:00:00Z",
        "payload": {
            "adapter_type": "http",
            "device_id": "lamp-001",
            "request_id": "req-lamp-on-001",
            "command_name": "turn_on",
        },
    }

    result = asyncio.run(module.run_gateway_job(ctx, job_message))

    assert result["status"] == "accepted"
    assert result["adapter_type"] == "http"
    assert client.completed[0][0] == "run-gateway-001"
    assert client.failed == []


def test_gateway_worker_fails_when_adapter_is_missing():
    module = _load_worker_module()
    client = _FakeManagementClient()
    ctx = {"management_client": client}
    job_message = {
        "job_run_id": "run-gateway-002",
        "schedule_id": "sched-gateway-002",
        "job_type": "device_command",
        "executor_type": "gateway",
        "scheduled_for": "2026-03-31T10:00:00Z",
        "payload": {
            "adapter_type": "zigbee",
            "device_id": "lamp-002",
            "request_id": "req-lamp-off-001",
            "command_name": "turn_off",
        },
    }

    result = asyncio.run(module.run_gateway_job(ctx, job_message))

    assert result["status"] == "failed"
    assert result["error"] == "adapter_not_found"
    assert client.completed == []
    assert client.failed[0][0] == "run-gateway-002"
