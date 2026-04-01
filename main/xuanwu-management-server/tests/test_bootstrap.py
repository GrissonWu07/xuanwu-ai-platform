from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import pytest
from aiohttp import web


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


def test_create_app_returns_aiohttp_application():
    module = _load_management_app_module()

    config = {"server": {"http_port": 18080}}
    app = module.create_app(config)

    assert isinstance(app, web.Application)


def test_load_runtime_config_uses_expected_defaults(monkeypatch: pytest.MonkeyPatch):
    module = _load_management_app_module()

    monkeypatch.delenv("XUANWU_MANAGEMENT_SERVER_HOST", raising=False)
    monkeypatch.delenv("XUANWU_MANAGEMENT_SERVER_PORT", raising=False)
    monkeypatch.delenv("XUANWU_MANAGEMENT_SERVER_AUTH_KEY", raising=False)
    monkeypatch.delenv("XUANWU_BASE_URL", raising=False)
    monkeypatch.delenv("XUANWU_CONTROL_PLANE_SECRET", raising=False)

    config = module.load_runtime_config()

    assert config["server"]["host"] == "0.0.0.0"
    assert config["server"]["http_port"] == 18082
    assert config["server"]["auth_key"] == "xuanwu-management-local-secret"
    assert config["xuanwu"]["base_url"] == "http://xuanwu-ai:8000"
    assert config["xuanwu"]["control_plane_secret"] == "xuanwu-management-to-xuanwu"


def test_main_uses_environment_overrides_for_runtime_config(
    monkeypatch: pytest.MonkeyPatch,
):
    module = _load_management_app_module()

    captured: dict[str, object] = {}

    def fake_create_app(config: dict):
        captured["config"] = config
        return web.Application()

    def fake_run_app(app, *, host: str, port: int):
        captured["host"] = host
        captured["port"] = port
        captured["app"] = app

    monkeypatch.setattr(module, "create_app", fake_create_app)
    monkeypatch.setattr(module.web, "run_app", fake_run_app)
    monkeypatch.setenv("XUANWU_MANAGEMENT_SERVER_HOST", "127.0.0.1")
    monkeypatch.setenv("XUANWU_MANAGEMENT_SERVER_PORT", "19082")
    monkeypatch.setenv("XUANWU_MANAGEMENT_SERVER_AUTH_KEY", "mgmt-secret-19082")
    monkeypatch.setenv("XUANWU_BASE_URL", "http://127.0.0.1:18000")
    monkeypatch.setenv("XUANWU_CONTROL_PLANE_SECRET", "cp-to-xuanwu-19082")

    module.main()

    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 19082
    assert captured["config"] == {
        "server": {
            "host": "127.0.0.1",
            "http_port": 19082,
            "auth_key": "mgmt-secret-19082",
        },
        "control-plane": {
            "secret": "mgmt-secret-19082",
            "backend": "postgres",
            "postgres": {
                "host": "postgres",
                "port": 5432,
                "database": "xuanwu_platform",
                "user": "xuanwu",
                "password": "xuanwu_local_password",
                "schema": "xw_mgmt",
            },
        },
        "xuanwu": {
            "base_url": "http://127.0.0.1:18000",
            "control_plane_secret": "cp-to-xuanwu-19082",
        },
    }
