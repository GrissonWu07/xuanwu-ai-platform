from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def _load_http_adapter_module():
    root = Path(__file__).resolve().parents[3]
    module_path = root / "main" / "xuanwu-gateway" / "core" / "adapters" / "http_adapter.py"
    service_root = module_path.parents[2]

    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for module_name in list(sys.modules):
        if module_name == "config" or module_name.startswith("config."):
            sys.modules.pop(module_name, None)
        if module_name == "core" or module_name.startswith("core."):
            sys.modules.pop(module_name, None)

    spec = spec_from_file_location("xuanwu_gateway_http_adapter", module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeHttpTransport:
    def __init__(self, response):
        self.response = response
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
        return self.response


def test_http_adapter_executes_real_http_shaped_command():
    module = _load_http_adapter_module()
    transport = FakeHttpTransport(
        {
            "status_code": 200,
            "body": {"ok": True, "power": "on"},
            "headers": {"content-type": "application/json"},
        }
    )
    adapter = module.HttpAdapter(transport=transport)

    command = {
        "request_id": "req-http-001",
        "gateway_id": "gateway-http-001",
        "adapter_type": "http",
        "device_id": "device-http-001",
        "capability_code": "switch.on_off",
        "command_name": "turn_on",
        "arguments": {"state": True},
        "route": {
            "url": "http://device.local/api/power",
            "method": "POST",
            "headers": {"Authorization": "Bearer token-http-001"},
            "body_template": {"power": "{arguments.state}"},
            "timeout_ms": 2500,
        },
    }

    result = adapter.dispatch(command)

    assert result["status"] == "succeeded"
    assert result["result"]["protocol_response"]["ok"] is True
    assert transport.calls[0]["method"] == "POST"
    assert transport.calls[0]["url"] == "http://device.local/api/power"
    assert transport.calls[0]["headers"]["Authorization"] == "Bearer token-http-001"
    assert transport.calls[0]["json_body"] == {"power": True}
    assert transport.calls[0]["timeout_ms"] == 2500


def test_http_adapter_normalizes_http_error_response():
    module = _load_http_adapter_module()
    transport = FakeHttpTransport(
        {
            "status_code": 503,
            "body": {"message": "device unavailable"},
            "headers": {"content-type": "application/json"},
        }
    )
    adapter = module.HttpAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-http-002",
            "gateway_id": "gateway-http-001",
            "adapter_type": "http",
            "device_id": "device-http-002",
            "capability_code": "switch.on_off",
            "command_name": "turn_off",
            "arguments": {"state": False},
            "route": {
                "url": "http://device.local/api/power",
                "method": "POST",
                "body_template": {"power": "{arguments.state}"},
            },
        }
    )

    assert result["status"] == "failed"
    assert result["error"]["code"] == "http_request_failed"
    assert result["error"]["details"]["status_code"] == 503
