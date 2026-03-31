import asyncio
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def _load_worker_module():
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-jobs" / "core" / "management_worker.py"
    service_root = module_path.parents[1]

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for module_name in list(sys.modules):
        if module_name == "config" or module_name.startswith("config."):
            sys.modules.pop(module_name, None)
        if module_name == "core" or module_name.startswith("core."):
            sys.modules.pop(module_name, None)

    spec = spec_from_file_location("xuanwu_jobs_management_worker", module_path)
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


def test_management_worker_completes_supported_management_job_types():
    module = _load_worker_module()
    client = _FakeManagementClient()
    ctx = {"management_client": client}
    job_message = {
        "job_run_id": "run-alarm-001",
        "schedule_id": "sched-alarm-001",
        "job_type": "alarm_escalation",
        "executor_type": "management",
        "scheduled_for": "2026-03-31T10:00:00Z",
        "payload": {"alarm_id": "alarm-001", "severity": "warning"},
    }

    result = asyncio.run(module.run_management_job(ctx, job_message))

    assert result["status"] == "completed"
    assert client.completed == [
        (
            "run-alarm-001",
            {
                "status": "completed",
                "job_type": "alarm_escalation",
                "result": {
                    "alarm_id": "alarm-001",
                    "severity": "warning",
                    "status": "completed",
                },
            },
        )
    ]
    assert client.failed == []


def test_management_worker_marks_unknown_job_type_failed():
    module = _load_worker_module()
    client = _FakeManagementClient()
    ctx = {"management_client": client}
    job_message = {
        "job_run_id": "run-agent-001",
        "schedule_id": "sched-agent-001",
        "job_type": "agent_run",
        "executor_type": "management",
        "scheduled_for": "2026-03-31T10:00:00Z",
        "payload": {"agent_id": "agent-001"},
    }

    result = asyncio.run(module.run_management_job(ctx, job_message))

    assert result["status"] == "failed"
    assert client.completed == []
    assert client.failed == [
        (
            "run-agent-001",
            {
                "status": "failed",
                "job_type": "agent_run",
                "error": "unsupported_management_job_type",
            },
        )
    ]
