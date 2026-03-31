from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def _load_management_app_module():
    root = Path(__file__).resolve().parents[3]
    app_path = root / "main" / "xuanwu-management-server" / "app.py"
    service_root = app_path.parent

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for module_name in list(sys.modules):
        if module_name == "config" or module_name.startswith("config."):
            sys.modules.pop(module_name, None)
        if module_name == "core" or module_name.startswith("core."):
            sys.modules.pop(module_name, None)

    spec = spec_from_file_location("xuanwu_management_server_app", app_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_create_app_registers_control_plane_routes():
    module = _load_management_app_module()

    app = module.create_app(
        {
            "server": {"auth_key": "runtime-secret"},
            "control-plane": {},
        }
    )
    registered_paths = sorted(
        route.resource.canonical for route in app.router.routes() if hasattr(route.resource, "canonical")
    )

    assert "/control-plane/v1/config/server" in registered_paths
    assert "/control-plane/v1/auth/login" in registered_paths
    assert "/control-plane/v1/auth/logout" in registered_paths
    assert "/control-plane/v1/devices" in registered_paths
    assert "/control-plane/v1/devices:batch-import" in registered_paths
    assert "/control-plane/v1/devices/{device_id}" in registered_paths
    assert "/control-plane/v1/devices/{device_id}:claim" in registered_paths
    assert "/control-plane/v1/devices/{device_id}:bind" in registered_paths
    assert "/control-plane/v1/devices/{device_id}:suspend" in registered_paths
    assert "/control-plane/v1/devices/{device_id}:retire" in registered_paths
    assert "/control-plane/v1/agents/{agent_id}" in registered_paths
    assert "/control-plane/v1/users" in registered_paths
    assert "/control-plane/v1/users/{user_id}" in registered_paths
    assert "/control-plane/v1/channels" in registered_paths
    assert "/control-plane/v1/channels/{channel_id}" in registered_paths
    assert "/control-plane/v1/events" in registered_paths
    assert "/control-plane/v1/events/{event_id}" in registered_paths
    assert "/control-plane/v1/telemetry" in registered_paths
    assert "/control-plane/v1/alarms" in registered_paths
    assert "/control-plane/v1/alarms/{alarm_id}:ack" in registered_paths
    assert "/control-plane/v1/gateways" in registered_paths
    assert "/control-plane/v1/gateways/{gateway_id}" in registered_paths
    assert "/control-plane/v1/mappings/user-devices" in registered_paths
    assert "/control-plane/v1/mappings/user-channels" in registered_paths
    assert "/control-plane/v1/mappings/channel-devices" in registered_paths
    assert "/control-plane/v1/mappings/device-agents" in registered_paths
    assert "/control-plane/v1/mappings/agent-model-providers" in registered_paths
    assert "/control-plane/v1/mappings/agent-model-configs" in registered_paths
    assert "/control-plane/v1/mappings/agent-knowledge" in registered_paths
    assert "/control-plane/v1/mappings/agent-workflows" in registered_paths
    assert "/control-plane/v1/capabilities" in registered_paths
    assert "/control-plane/v1/capability-routes" in registered_paths
    assert "/control-plane/v1/ota/firmwares" in registered_paths
    assert "/control-plane/v1/ota/firmwares/{firmware_id}" in registered_paths
    assert "/control-plane/v1/ota/campaigns" in registered_paths
    assert "/control-plane/v1/runtime/device-config:resolve" in registered_paths
    assert "/control-plane/v1/runtime/devices/{device_id}/binding-view" in registered_paths
    assert "/control-plane/v1/runtime/devices/{device_id}/capability-routing-view" in registered_paths
    assert "/control-plane/v1/chat-history/report" in registered_paths
    assert "/control-plane/v1/chat-summaries/{summary_id}:generate" in registered_paths
    assert "/control-plane/v1/gateway/events" in registered_paths
    assert "/control-plane/v1/gateway/telemetry" in registered_paths
    assert "/control-plane/v1/gateway/command-results" in registered_paths
    assert "/control-plane/v1/jobs/schedules" in registered_paths
    assert "/control-plane/v1/jobs/schedules:due" in registered_paths
    assert "/control-plane/v1/jobs/schedules/{schedule_id}:claim" in registered_paths
    assert "/control-plane/v1/jobs/runs" in registered_paths
    assert "/control-plane/v1/jobs/runs/{job_run_id}:complete" in registered_paths
    assert "/control-plane/v1/jobs/runs/{job_run_id}:fail" in registered_paths
