from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def test_load_runtime_config_reads_postgres_env(monkeypatch):
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

    monkeypatch.setenv("XUANWU_PG_HOST", "postgres")
    monkeypatch.setenv("XUANWU_PG_PORT", "5432")
    monkeypatch.setenv("XUANWU_PG_DB", "xuanwu_platform")
    monkeypatch.setenv("XUANWU_PG_USER", "xuanwu")
    monkeypatch.setenv("XUANWU_PG_PASSWORD", "secret")
    monkeypatch.setenv("XUANWU_MGMT_PG_SCHEMA", "xw_mgmt")

    config = module.load_runtime_config()

    assert config["control-plane"]["backend"] == "postgres"
    assert config["control-plane"]["postgres"]["host"] == "postgres"
    assert config["control-plane"]["postgres"]["schema"] == "xw_mgmt"
