from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def _load_registry_module():
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-iot-gateway" / "core" / "registry" / "adapter_registry.py"
    service_root = module_path.parents[2]

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for module_name in list(sys.modules):
        if module_name == "config" or module_name.startswith("config."):
            sys.modules.pop(module_name, None)
        if module_name == "core" or module_name.startswith("core."):
            sys.modules.pop(module_name, None)

    spec = spec_from_file_location("xuanwu_gateway_registry", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_registry_lists_builtin_adapters():
    registry = _load_registry_module().create_builtin_registry()

    adapter_types = sorted(item["adapter_type"] for item in registry.describe())

    assert adapter_types == [
        "bacnet_ip",
        "bluetooth",
        "can_gateway",
        "home_assistant",
        "http",
        "modbus_tcp",
        "mqtt",
        "nearlink",
        "opc_ua",
        "sensor_http_push",
        "sensor_mqtt",
    ]


def test_builtin_adapters_describe_themselves():
    registry = _load_registry_module().create_builtin_registry()

    descriptions = {item["adapter_type"]: item for item in registry.describe()}

    assert descriptions["http"]["supports_dry_run"] is True
    assert descriptions["mqtt"]["supports_dry_run"] is True
    assert descriptions["home_assistant"]["supports_dry_run"] is True
    assert descriptions["http"]["supports_ingest"] is False
    assert descriptions["mqtt"]["supported_capabilities"]
    assert descriptions["home_assistant"]["supported_capabilities"]
