from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEVICE_SERVER = ROOT / "main" / "xuanwu-device-gateway"


def test_legacy_manager_compatibility_files_are_removed_from_device_server():
    assert not (DEVICE_SERVER / "config" / "manage_api_client.py").exists()
    assert not (DEVICE_SERVER / "core" / "api" / "control_plane_handler.py").exists()
    assert not (DEVICE_SERVER / "scripts" / "import_control_plane_bundle.py").exists()
    compat_python_files = list((DEVICE_SERVER / "core" / "control_plane").glob("*.py"))
    assert compat_python_files == []


def test_runtime_python_sources_do_not_reference_legacy_manager_api_symbols():
    source_files = [
        DEVICE_SERVER / "app.py",
        DEVICE_SERVER / "config" / "config_loader.py",
        DEVICE_SERVER / "core" / "connection.py",
        DEVICE_SERVER / "core" / "handle" / "reportHandle.py",
        DEVICE_SERVER / "core" / "handle" / "textHandler" / "serverMessageHandler.py",
        DEVICE_SERVER / "core" / "http_server.py",
        DEVICE_SERVER
        / "core"
        / "providers"
        / "memory"
        / "mem_local_short"
        / "mem_local_short.py",
    ]

    for source_file in source_files:
        content = source_file.read_text(encoding="utf-8")
        assert "manage_api_client" not in content, source_file
        assert "is_manager_api_enabled" not in content, source_file
        assert "manager-api" not in content, source_file
