import asyncio
import sys
import types
from pathlib import Path

from aiohttp.test_utils import make_mocked_request


SERVICE_ROOT = Path(__file__).resolve().parents[1]


def _load_runtime_module():
    while str(SERVICE_ROOT) in sys.path:
        sys.path.remove(str(SERVICE_ROOT))
    sys.path.insert(0, str(SERVICE_ROOT))
    for loaded_name in list(sys.modules):
        if loaded_name == "config" or loaded_name.startswith("config."):
            sys.modules.pop(loaded_name, None)
        if loaded_name == "core" or loaded_name.startswith("core."):
            sys.modules.pop(loaded_name, None)

    fake_logger_module = types.ModuleType("config.logger")
    fake_logger_module.setup_logging = lambda: None
    sys.modules["config.logger"] = fake_logger_module

    import core.api.runtime_handler as runtime_module

    return runtime_module


class _DummyDialogue:
    def __init__(self):
        self.messages = []

    def put(self, message):
        self.messages.append(message)


class _DummyQueue:
    def __init__(self):
        self.items = []

    def put(self, item):
        self.items.append(item)


class _DummyTTS:
    def __init__(self):
        self.tts_text_queue = _DummyQueue()
        self.calls = []

    def tts_one_sentence(self, conn, content_type, content_detail=None):
        self.calls.append((content_type, content_detail))


class _DummyAction:
    name = "EXECUTED"


class _DummyToolResult:
    action = _DummyAction()
    response = "tool ok"
    result = {"ok": True}


class _DummyFuncHandler:
    def __init__(self, *, finish_init=True, has_tool=True):
        self.finish_init = finish_init
        self._has_tool = has_tool

    def current_support_functions(self):
        return ["self_camera_take_photo", "switch_on"]

    def has_tool(self, name):
        return self._has_tool and name in {"self_camera_take_photo", "switch_on"}

    async def handle_llm_function_call(self, conn, payload):
        return _DummyToolResult()


class _DummyConn:
    def __init__(self):
        self.tts = _DummyTTS()
        self.features = {"vision": True}
        self.iot_descriptors = {"switch": {"state": "off"}}
        self.client_is_speaking = False
        self.client_listen_mode = "auto"
        self.need_bind = False
        self.func_handler = _DummyFuncHandler()
        self.dialogue = _DummyDialogue()
        self.headers = {"client-id": "client-001", "x-firmware-version": "fw-1.0.0"}
        self.device_id = "dev-001"
        self.runtime_session_id = "runtime-001"
        self.sample_rate = 16000
        self.audio_format = "opus"
        self.client_abort = False
        self.websocket = types.SimpleNamespace(closed=False)
        self.tts_MessageText = ""
        self.sentence_id = ""


def test_runtime_handler_rejects_invalid_secret_and_missing_session():
    module = _load_runtime_module()
    handler = module.RuntimeHandler({"server": {"auth_key": "runtime-secret"}})

    bad_secret_request = make_mocked_request(
        "GET",
        "/runtime/v1/sessions/runtime-001/context",
        headers={"X-Xuanwu-Runtime-Secret": "wrong"},
        match_info={"runtime_session_id": "runtime-001"},
    )
    missing_session_request = make_mocked_request(
        "GET",
        "/runtime/v1/sessions/runtime-404/context",
        headers={"X-Xuanwu-Runtime-Secret": "runtime-secret"},
        match_info={"runtime_session_id": "runtime-404"},
    )

    bad_secret_response = asyncio.run(handler.handle_context(bad_secret_request))
    missing_session_response = asyncio.run(handler.handle_context(missing_session_request))

    assert bad_secret_response.status == 401
    assert missing_session_response.status == 404


def test_runtime_handler_tool_execution_and_speak_paths():
    module = _load_runtime_module()
    handler = module.RuntimeHandler({"server": {"auth_key": "runtime-secret"}})
    conn = _DummyConn()
    record = module.RuntimeSessionRecord(
        runtime_session_id="runtime-001",
        device_id="dev-001",
        client_id="client-001",
        xuanwu_session_key="session-001",
        conn=conn,
    )
    handler._load_record = lambda runtime_session_id: (record, None)

    missing_tool_name_request = make_mocked_request(
        "POST",
        "/runtime/v1/sessions/runtime-001/tool-executions",
        headers={"X-Xuanwu-Runtime-Secret": "runtime-secret"},
        match_info={"runtime_session_id": "runtime-001"},
    )
    missing_tool_name_request._read_bytes = b'{"arguments":{}}'
    missing_tool_name_response = asyncio.run(handler.handle_tool_execution(missing_tool_name_request))

    not_ready_conn = _DummyConn()
    not_ready_conn.func_handler = _DummyFuncHandler(finish_init=False)
    not_ready_record = module.RuntimeSessionRecord(
        runtime_session_id="runtime-002",
        device_id="dev-002",
        client_id="client-002",
        xuanwu_session_key="session-002",
        conn=not_ready_conn,
    )
    handler._load_record = lambda runtime_session_id: (not_ready_record, None)
    not_ready_request = make_mocked_request(
        "POST",
        "/runtime/v1/sessions/runtime-002/tool-executions",
        headers={"X-Xuanwu-Runtime-Secret": "runtime-secret"},
        match_info={"runtime_session_id": "runtime-002"},
    )
    not_ready_request._read_bytes = b'{"name":"switch_on","arguments":{}}'
    not_ready_response = asyncio.run(handler.handle_tool_execution(not_ready_request))

    handler._load_record = lambda runtime_session_id: (record, None)
    tool_request = make_mocked_request(
        "POST",
        "/runtime/v1/sessions/runtime-001/tool-executions",
        headers={"X-Xuanwu-Runtime-Secret": "runtime-secret"},
        match_info={"runtime_session_id": "runtime-001"},
    )
    tool_request._read_bytes = b'{"name":"switch_on","arguments":{"power":"on"},"request_id":"req-001"}'
    tool_response = asyncio.run(handler.handle_tool_execution(tool_request))

    speak_request = make_mocked_request(
        "POST",
        "/runtime/v1/sessions/runtime-001/speak",
        headers={"X-Xuanwu-Runtime-Secret": "runtime-secret"},
        match_info={"runtime_session_id": "runtime-001"},
    )
    speak_request._read_bytes = b'{"text":"hello world","interrupt_current":false}'
    speak_response = asyncio.run(handler.handle_speak(speak_request))

    assert missing_tool_name_response.status == 400
    assert not_ready_response.status == 409
    assert tool_response.status == 200
    assert '"request_id":"req-001"' in tool_response.text
    assert speak_response.status == 200
    assert conn.tts.calls


def test_runtime_handler_interrupt_and_gone_session_paths():
    module = _load_runtime_module()
    handler = module.RuntimeHandler({"server": {"auth_key": "runtime-secret"}})
    conn = _DummyConn()
    record = module.RuntimeSessionRecord(
        runtime_session_id="runtime-003",
        device_id="dev-003",
        client_id="client-003",
        xuanwu_session_key="session-003",
        conn=conn,
    )

    aborted = {"called": False}

    async def fake_abort(target_conn):
        aborted["called"] = target_conn is conn

    module.handleAbortMessage = fake_abort
    handler._load_record = lambda runtime_session_id: (record, None)
    interrupt_request = make_mocked_request(
        "POST",
        "/runtime/v1/sessions/runtime-003:interrupt",
        headers={"X-Xuanwu-Runtime-Secret": "runtime-secret"},
        match_info={"runtime_session_id": "runtime-003"},
    )
    interrupt_response = asyncio.run(handler.handle_interrupt(interrupt_request))
    del handler._load_record

    gone_conn = _DummyConn()
    gone_conn.websocket = None
    module.runtime_session_registry.register(
        "runtime-gone",
        device_id="dev-gone",
        client_id="client-gone",
        xuanwu_session_key="session-gone",
        conn=gone_conn,
    )
    gone_request = make_mocked_request(
        "GET",
        "/runtime/v1/sessions/runtime-gone/context",
        headers={"X-Xuanwu-Runtime-Secret": "runtime-secret"},
        match_info={"runtime_session_id": "runtime-gone"},
    )
    gone_response = asyncio.run(handler.handle_context(gone_request))

    assert interrupt_response.status == 200
    assert aborted["called"] is True
    assert gone_response.status == 410


def test_runtime_handler_executes_device_job_with_real_payload_shape():
    module = _load_runtime_module()
    handler = module.RuntimeHandler({"server": {"auth_key": "runtime-secret"}})

    execute_request = make_mocked_request(
        "POST",
        "/runtime/v1/jobs:execute",
        headers={"X-Xuanwu-Runtime-Secret": "runtime-secret"},
    )
    execute_request._read_bytes = (
        b'{"job_run_id":"run-device-001","job_type":"runtime_config_refresh","executor_type":"device",'
        b'"payload":{"device_id":"dev-001","reason":"scheduled-refresh"}}'
    )

    response = asyncio.run(handler.handle_execute_job(execute_request))

    assert response.status == 200
    assert '"job_run_id":"run-device-001"' in response.text
    assert '"job_type":"runtime_config_refresh"' in response.text
