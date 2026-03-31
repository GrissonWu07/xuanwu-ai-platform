import asyncio
import importlib
from pathlib import Path
import sys


def _load_dispatcher_module():
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

    return importlib.import_module("core.dispatcher")


class _FakeClient:
    def __init__(self, response):
        self.calls = []
        self.response = response

    async def execute_job(self, job_message: dict):
        self.calls.append(job_message)
        return self.response


def test_dispatcher_routes_platform_gateway_and_device_jobs_to_matching_clients():
    module = _load_dispatcher_module()
    platform = _FakeClient({"status": "completed"})
    gateway = _FakeClient({"status": "accepted"})
    device = _FakeClient({"status": "completed"})
    dispatcher = module.JobDispatcher(
        management_client=platform,
        gateway_client=gateway,
        device_client=device,
    )

    platform_job = {"job_run_id": "run-platform-001", "executor_type": "platform", "job_type": "telemetry_rollup"}
    gateway_job = {"job_run_id": "run-gateway-001", "executor_type": "gateway", "job_type": "device_command"}
    device_job = {"job_run_id": "run-device-001", "executor_type": "device", "job_type": "runtime_config_refresh"}

    assert asyncio.run(dispatcher.dispatch(platform_job))["status"] == "completed"
    assert asyncio.run(dispatcher.dispatch(gateway_job))["status"] == "accepted"
    assert asyncio.run(dispatcher.dispatch(device_job))["status"] == "completed"
    assert platform.calls == [platform_job]
    assert gateway.calls == [gateway_job]
    assert device.calls == [device_job]


def test_dispatcher_rejects_agent_jobs_until_upstream_xuanwu_contract_is_ready():
    module = _load_dispatcher_module()
    dispatcher = module.JobDispatcher(
        management_client=_FakeClient({"status": "completed"}),
        gateway_client=_FakeClient({"status": "accepted"}),
        device_client=_FakeClient({"status": "completed"}),
    )

    result = asyncio.run(
        dispatcher.dispatch({"job_run_id": "run-agent-001", "executor_type": "agent", "job_type": "agent_run"})
    )

    assert result["status"] == "failed"
    assert result["error"] == "agent_executor_not_configured"


def test_dispatcher_rejects_unknown_executor_types():
    module = _load_dispatcher_module()
    dispatcher = module.JobDispatcher(
        management_client=_FakeClient({"status": "completed"}),
        gateway_client=_FakeClient({"status": "accepted"}),
        device_client=_FakeClient({"status": "completed"}),
    )

    result = asyncio.run(
        dispatcher.dispatch({"job_run_id": "run-unknown-001", "executor_type": "industrial", "job_type": "noop"})
    )

    assert result["status"] == "failed"
    assert result["error"] == "unsupported_executor_type"
