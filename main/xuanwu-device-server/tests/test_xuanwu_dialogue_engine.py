import asyncio
import sys
import types
from pathlib import Path


SERVICE_ROOT = Path(__file__).resolve().parents[1]


def _load_xuanwu_module():
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

    import core.providers.agent.xuanwu as xuanwu_module

    return xuanwu_module


class _DummyLogger:
    def bind(self, **kwargs):
        return self

    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None


class _DummyConn:
    def __init__(self):
        self.client_abort = False
        self.xuanwu_stream_task = None
        self.xuanwu_run_id = None
        self.runtime_session_id = "runtime-001"
        self.xuanwu_session_key = "session-001"
        self.device_id = "dev-001"
        self.headers = {"client-id": "client-001", "firmware-version": "fw-1.0.0"}
        self.audio_format = "opus"
        self.sample_rate = 16000
        self.need_bind = False
        self.tts = object()
        self.features = {"vision": True}
        self.iot_descriptors = {"switch": {"state": "off"}}
        self.config = {"locale": "zh-CN", "system_error_response": "fallback message"}
        self.logger = _DummyLogger()
        self.dialogue = types.SimpleNamespace(messages=[], put=lambda message: None)


class _FakeResponse:
    def __init__(self, payload=None, status=200):
        self.payload = payload or {}
        self.status = status
        self.content = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def raise_for_status(self):
        if self.status >= 400:
            raise RuntimeError(f"http {self.status}")

    async def json(self):
        return self.payload


class _FakeSession:
    def __init__(self):
        self.posts = []
        self.gets = []
        self.closed = False

    def post(self, url, **kwargs):
        self.posts.append((url, kwargs))
        if url.endswith("/agent/run"):
            return _FakeResponse({"run_id": "run-001"})
        return _FakeResponse({})

    def get(self, url, **kwargs):
        self.gets.append((url, kwargs))
        return _FakeResponse({})


def test_xuanwu_dialogue_engine_from_config_uses_fallback_without_base_url():
    module = _load_xuanwu_module()

    engine = module.XuanWuDialogueEngine.from_config(
        {
            "selected_module": {"Agent": "XuanWu"},
            "Agent": {"XuanWu": {}},
            "system_error_response": "fallback text",
        }
    )

    assert engine.__class__.__name__ == "TemplateFallbackDialogueEngine"


def test_xuanwu_dialogue_engine_builds_context_and_decodes_payload():
    module = _load_xuanwu_module()
    engine = module.XuanWuDialogueEngine(
        {
            "selected_module": {"Agent": "XuanWu"},
            "Agent": {"XuanWu": {"base_url": "http://xuanwu-ai:8000", "locale": "zh-CN"}},
        }
    )
    conn = _DummyConn()
    conn.func_handler = types.SimpleNamespace(
        finish_init=True,
        has_tool=lambda name: name == "self_camera_take_photo",
    )

    context = engine._build_context(conn)

    assert context["device_id"] == "dev-001"
    assert context["bind_status"] == "bound"
    assert context["capabilities"]["camera"] is True
    assert engine._decode_payload('{"text":"hello"}') == {"text": "hello"}
    assert engine._decode_payload("raw-text") == {"message": "raw-text"}


def test_xuanwu_dialogue_engine_session_and_abort_paths():
    module = _load_xuanwu_module()
    engine = module.XuanWuDialogueEngine(
        {
            "selected_module": {"Agent": "XuanWu"},
            "Agent": {"XuanWu": {"base_url": "http://xuanwu-ai:8000", "api_key": "key-001"}},
        }
    )
    fake_session = _FakeSession()
    conn = _DummyConn()

    async def scenario():
        engine._session = fake_session

        task = asyncio.create_task(asyncio.sleep(0.05), name="xuanwu-old-task")
        conn.xuanwu_stream_task = task
        conn.xuanwu_run_id = "run-old"
        await engine.abort_turn(conn)

        run_id = await engine._start_run(conn, "hello")
        return run_id

    run_id = asyncio.run(scenario())

    assert run_id == "run-001"
    assert fake_session.posts[0][0].endswith("/agent/runs/run-old/abort")
    assert fake_session.posts[1][0].endswith("/agent/run")


def test_xuanwu_dialogue_engine_consumes_stream_events():
    module = _load_xuanwu_module()
    engine = module.XuanWuDialogueEngine(
        {
            "selected_module": {"Agent": "XuanWu"},
            "Agent": {"XuanWu": {"base_url": "http://xuanwu-ai:8000"}},
        }
    )
    fake_session = _FakeSession()
    conn = _DummyConn()
    bridge_calls = {"text": [], "failed": []}

    class FakeBridge:
        def feed_text(self, text):
            bridge_calls["text"].append(text)

        def fail(self, message):
            bridge_calls["failed"].append(message)

    async def fake_iter_sse_events(response):
        yield "assistant", {"text": "hello"}
        yield "thinking", {"text": "..."}
        yield "error", {"message": "stream-error"}

    async def scenario():
        engine._session = fake_session
        engine._iter_sse_events = fake_iter_sse_events
        await engine._consume_stream(conn, "run-001", FakeBridge())

    asyncio.run(scenario())

    assert fake_session.gets[0][0].endswith("/agent/runs/run-001/stream")
    assert bridge_calls["text"] == ["hello"]
    assert bridge_calls["failed"] == ["stream-error"]
