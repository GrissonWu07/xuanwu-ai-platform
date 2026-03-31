from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def _load_home_assistant_module():
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-gateway" / "core" / "adapters" / "home_assistant_adapter.py"
    service_root = module_path.parents[2]

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for module_name in list(sys.modules):
        if module_name == "config" or module_name.startswith("config."):
            sys.modules.pop(module_name, None)
        if module_name == "core" or module_name.startswith("core."):
            sys.modules.pop(module_name, None)

    spec = spec_from_file_location("xuanwu_gateway_home_assistant_adapter", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeHttpTransport:
    def __init__(self):
        self.calls = []

    def request(self, *, method, url, headers, json_body, timeout_ms):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "json_body": json_body,
                "timeout_ms": timeout_ms,
            }
        )
        return {"status_code": 200, "body": {"changed_states": []}, "headers": {}}


def test_home_assistant_adapter_calls_service_endpoint():
    module = _load_home_assistant_module()
    transport = FakeHttpTransport()
    adapter = module.HomeAssistantAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-ha-001",
            "gateway_id": "gateway-ha-001",
            "adapter_type": "home_assistant",
            "device_id": "device-ha-light-001",
            "capability_code": "switch.on_off",
            "command_name": "turn_on",
            "arguments": {"brightness": 180},
            "route": {
                "base_url": "http://homeassistant.local:8123",
                "token": "ha-token-001",
                "service_domain": "light",
                "service_name": "turn_on",
                "entity_id": "light.living_room",
                "timeout_ms": 3000,
            },
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["method"] == "POST"
    assert (
        transport.calls[0]["url"]
        == "http://homeassistant.local:8123/api/services/light/turn_on"
    )
    assert transport.calls[0]["headers"]["Authorization"] == "Bearer ha-token-001"
    assert transport.calls[0]["json_body"]["entity_id"] == "light.living_room"
    assert transport.calls[0]["json_body"]["brightness"] == 180


def test_home_assistant_adapter_reads_entity_state():
    module = _load_home_assistant_module()

    class FakeStateTransport:
        def __init__(self):
            self.calls = []

        def request(self, *, method, url, headers, json_body, timeout_ms):
            self.calls.append(
                {
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "json_body": json_body,
                    "timeout_ms": timeout_ms,
                }
            )
            return {
                "status_code": 200,
                "body": {"state": "on", "attributes": {"brightness": 80}},
                "headers": {},
            }

    transport = FakeStateTransport()
    adapter = module.HomeAssistantAdapter(transport=transport)
    result = adapter.dispatch(
        {
            "request_id": "req-ha-read-001",
            "gateway_id": "gateway-ha-001",
            "adapter_type": "home_assistant",
            "device_id": "ha-light-001",
            "capability_code": "home_assistant.state",
            "command_name": "read_state",
            "route": {
                "base_url": "http://ha.local:8123",
                "token": "secret-token",
                "entity_id": "light.living_room",
            },
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["method"] == "GET"
    assert transport.calls[0]["url"] == "http://ha.local:8123/api/states/light.living_room"
    assert result["result"]["protocol_response"]["state"] == "on"
