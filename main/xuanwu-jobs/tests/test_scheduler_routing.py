import asyncio
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def _load_scheduler_module():
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-jobs" / "core" / "scheduler.py"
    service_root = module_path.parents[1]

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for module_name in list(sys.modules):
        if module_name == "config" or module_name.startswith("config."):
            sys.modules.pop(module_name, None)
        if module_name == "core" or module_name.startswith("core."):
            sys.modules.pop(module_name, None)

    spec = spec_from_file_location("xuanwu_jobs_scheduler_routing", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _FakeManagementClient:
    def __init__(self):
        self._index = 0

    async def list_due_schedules(self, *, now_iso: str, limit: int):
        return {
            "items": [
                {
                    "schedule_id": "sched-mgmt-001",
                    "job_type": "alarm_escalation",
                    "executor_type": "management",
                    "next_run_at": "2026-03-31T10:00:00Z",
                    "payload": {"alarm_id": "alarm-001"},
                },
                {
                    "schedule_id": "sched-gateway-001",
                    "job_type": "device_command",
                    "executor_type": "gateway",
                    "next_run_at": "2026-03-31T10:00:00Z",
                    "payload": {"adapter_type": "http", "device_id": "lamp-001"},
                },
                {
                    "schedule_id": "sched-device-001",
                    "job_type": "runtime_config_refresh",
                    "executor_type": "device",
                    "next_run_at": "2026-03-31T10:00:00Z",
                    "payload": {"reason": "ops-refresh"},
                },
            ]
        }

    async def claim_schedule(self, schedule_id: str, *, scheduled_for: str):
        payloads = {
            "sched-mgmt-001": {
                "job_run_id": "run-mgmt-001",
                "schedule_id": "sched-mgmt-001",
                "job_type": "alarm_escalation",
                "executor_type": "management",
                "scheduled_for": scheduled_for,
                "payload": {"alarm_id": "alarm-001"},
            },
            "sched-gateway-001": {
                "job_run_id": "run-gateway-001",
                "schedule_id": "sched-gateway-001",
                "job_type": "device_command",
                "executor_type": "gateway",
                "scheduled_for": scheduled_for,
                "payload": {"adapter_type": "http", "device_id": "lamp-001"},
            },
            "sched-device-001": {
                "job_run_id": "run-device-001",
                "schedule_id": "sched-device-001",
                "job_type": "runtime_config_refresh",
                "executor_type": "device",
                "scheduled_for": scheduled_for,
                "payload": {"reason": "ops-refresh"},
            },
        }
        return payloads[schedule_id]


class _FakeRedisQueue:
    def __init__(self):
        self.calls = []

    async def enqueue_job(self, function_name: str, message: dict, *, _queue_name: str):
        self.calls.append((function_name, _queue_name, message["job_run_id"]))
        return {"job_id": f"redis-{message['job_run_id']}"}


def test_scheduler_routes_management_gateway_and_device_jobs_to_correct_queues():
    module = _load_scheduler_module()
    scheduler = module.JobScheduler(
        client=_FakeManagementClient(),
        redis_queue=_FakeRedisQueue(),
        config={
            "jobs": {
                "queue_names": {
                    "platform": "management",
                    "management": "management",
                    "gateway": "gateway",
                    "device": "device",
                },
                "schedule_batch_size": 50,
            }
        },
    )

    asyncio.run(
        scheduler.run_once(now=datetime(2026, 3, 31, 10, 0, 0, tzinfo=timezone.utc))
    )

    assert scheduler.redis_queue.calls == [
        ("run_management_job", "management", "run-mgmt-001"),
        ("run_gateway_job", "gateway", "run-gateway-001"),
        ("run_device_job", "device", "run-device-001"),
    ]
