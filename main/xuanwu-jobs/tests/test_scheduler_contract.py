import asyncio
from datetime import datetime, timezone
import importlib
from pathlib import Path
import sys


def _load_scheduler_module():
    root = Path(__file__).resolve().parents[3]
    service_root = root / "main" / "xuanwu-jobs"

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for module_name in list(sys.modules):
        if module_name == "config" or module_name.startswith("config."):
            sys.modules.pop(module_name, None)
        if module_name == "core" or module_name.startswith("core."):
            sys.modules.pop(module_name, None)

    return importlib.import_module("core.scheduler")


class _FakeManagementClient:
    def __init__(self):
        self.claim_calls = []
        self.run_claim_calls = []

    async def list_due_schedules(self, *, now_iso: str, limit: int):
        assert now_iso.startswith("2026-03-31T")
        assert limit == 50
        return {
            "items": [
                {
                    "schedule_id": "sched-telemetry-001",
                    "job_type": "telemetry_rollup",
                    "executor_type": "platform",
                    "next_run_at": "2026-03-31T10:00:00Z",
                    "payload": {"site_id": "site-a"},
                }
            ]
        }

    async def claim_schedule(self, schedule_id: str, *, scheduled_for: str):
        self.claim_calls.append((schedule_id, scheduled_for))
        return {
            "job_run_id": "run-sched-telemetry-001-20260331T100000Z",
            "schedule_id": schedule_id,
            "job_type": "telemetry_rollup",
            "executor_type": "platform",
            "scheduled_for": scheduled_for,
            "payload": {"site_id": "site-a"},
        }

    async def list_dispatchable_job_runs(self, *, now_iso: str, limit: int):
        return {
            "items": [
                {
                    "job_run_id": "run-manual-001",
                    "schedule_id": "sched-manual-001",
                    "job_type": "alarm_escalation",
                    "executor_type": "management",
                    "scheduled_for": "2026-03-31T10:00:00Z",
                    "status": "queued",
                    "payload": {"alarm_id": "alarm-001"},
                }
            ]
        }

    async def claim_job_run(self, job_run_id: str, *, started_at: str):
        self.run_claim_calls.append((job_run_id, started_at))
        return {
            "job_run_id": job_run_id,
            "schedule_id": "sched-manual-001",
            "job_type": "alarm_escalation",
            "executor_type": "management",
            "scheduled_for": "2026-03-31T10:00:00Z",
            "started_at": started_at,
            "status": "running",
            "payload": {"alarm_id": "alarm-001"},
        }

class _FakeDispatcher:
    def __init__(self):
        self.calls = []

    async def dispatch(self, claimed_job: dict):
        self.calls.append(claimed_job)
        return {"status": "completed", "executor_type": claimed_job["executor_type"]}


def test_scheduler_claims_due_schedule_and_dispatches_platform_job():
    module = _load_scheduler_module()
    scheduler = module.JobScheduler(
        client=_FakeManagementClient(),
        dispatcher=_FakeDispatcher(),
        config={"jobs": {"schedule_batch_size": 50}},
    )

    asyncio.run(
        scheduler.run_once(now=datetime(2026, 3, 31, 10, 0, 0, tzinfo=timezone.utc))
    )

    assert scheduler.client.claim_calls == [
        ("sched-telemetry-001", "2026-03-31T10:00:00Z")
    ]
    assert scheduler.client.run_claim_calls == [
        ("run-manual-001", "2026-03-31T10:00:00Z")
    ]
    assert scheduler.dispatcher.calls == [
        {
            "job_run_id": "run-sched-telemetry-001-20260331T100000Z",
            "schedule_id": "sched-telemetry-001",
            "job_type": "telemetry_rollup",
            "executor_type": "platform",
            "scheduled_for": "2026-03-31T10:00:00Z",
            "payload": {"site_id": "site-a"},
        },
        {
            "job_run_id": "run-manual-001",
            "schedule_id": "sched-manual-001",
            "job_type": "alarm_escalation",
            "executor_type": "management",
            "scheduled_for": "2026-03-31T10:00:00Z",
            "started_at": "2026-03-31T10:00:00Z",
            "status": "running",
            "payload": {"alarm_id": "alarm-001"},
        }
    ]
