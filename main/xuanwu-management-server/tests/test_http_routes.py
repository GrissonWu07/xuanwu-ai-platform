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
    assert "/control-plane/v1/devices/{device_id}" in registered_paths
    assert "/control-plane/v1/agents/{agent_id}" in registered_paths
    assert "/control-plane/v1/runtime/device-config:resolve" in registered_paths
