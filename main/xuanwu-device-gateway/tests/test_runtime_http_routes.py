from pathlib import Path
import asyncio
from importlib.util import module_from_spec, spec_from_file_location
import sys
import types

from aiohttp.test_utils import make_mocked_request


def test_runtime_http_server_no_longer_hosts_control_plane_routes():
    http_server_path = (
        Path(__file__).resolve().parents[1] / "core" / "http_server.py"
    )
    content = http_server_path.read_text(encoding="utf-8")

    assert "/control-plane/v1/" not in content
    assert "/runtime/v1/jobs:execute" in content


def _load_module(module_path: Path, module_name: str):
    service_root = Path(__file__).resolve().parents[1]
    while str(service_root) in sys.path:
        sys.path.remove(str(service_root))
    sys.path.insert(0, str(service_root))
    for loaded_name in list(sys.modules):
        if loaded_name == "config" or loaded_name.startswith("config."):
            sys.modules.pop(loaded_name, None)
        if loaded_name == "core" or loaded_name.startswith("core."):
            sys.modules.pop(loaded_name, None)

    fake_logger_module = types.ModuleType("config.logger")
    fake_logger_module.setup_logging = lambda: None
    sys.modules["config.logger"] = fake_logger_module

    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_runtime_session_key_exports_xuanwu_builder():
    module = _load_module(
        Path(__file__).resolve().parents[1] / "core" / "runtime" / "session_key.py",
        "xuanwu_device_server_session_key",
    )

    assert hasattr(module, "build_xuanwu_session_key")
    assert not hasattr(module, "build_atlas_session_key")
    session_key = module.build_xuanwu_session_key("dev-001", "client-001")
    assert session_key.endswith(":topic:client-001")


def test_runtime_handler_context_returns_xuanwu_session_key():
    module = _load_module(
        Path(__file__).resolve().parents[1] / "core" / "api" / "runtime_handler.py",
        "xuanwu_device_server_runtime_handler",
    )

    handler = module.RuntimeHandler({"server": {"auth_key": "runtime-secret"}})

    class DummyConn:
        tts = None
        features = None
        iot_descriptors = {}
        client_is_speaking = False
        client_listen_mode = "auto"
        need_bind = False

    dummy_record = module.RuntimeSessionRecord(
        runtime_session_id="runtime-001",
        device_id="dev-001",
        client_id="client-001",
        xuanwu_session_key="agent:main:user:device-dev-001:xuanwu:dm:dev-001:topic:client-001",
        conn=DummyConn(),
    )

    handler._load_record = lambda runtime_session_id: (dummy_record, None)
    request = make_mocked_request(
        "GET",
        "/runtime/v1/sessions/runtime-001/context",
        headers={"X-Xuanwu-Runtime-Secret": "runtime-secret"},
        match_info={"runtime_session_id": "runtime-001"},
    )

    response = asyncio.run(handler.handle_context(request))
    assert response.status == 200
    assert '"xuanwu_session_key":"agent:main:user:device-dev-001:xuanwu:dm:dev-001:topic:client-001"' in response.text
    assert "atlas_session_key" not in response.text
