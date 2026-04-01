from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_bluetooth_bridge_layout_and_packaging_assets_exist():
    bridge_root = ROOT / "main" / "xuanwu-bluetooth-bridge"
    assert (bridge_root / "app.py").exists()
    assert (bridge_root / "core" / "runtime.py").exists()
    assert (bridge_root / "core" / "api" / "bridge_handler.py").exists()
    assert (bridge_root / "packaging" / "linux" / "xuanwu-bluetooth-bridge.service").exists()
    assert (bridge_root / "packaging" / "linux" / "xuanwu-bluetooth-bridge.spec").exists()
    assert (bridge_root / "packaging" / "windows" / "install-service.ps1").exists()
    assert (bridge_root / "packaging" / "windows" / "service_wrapper.py").exists()


def test_nearlink_bridge_layout_and_packaging_assets_exist():
    bridge_root = ROOT / "main" / "xuanwu-nearlink-bridge"
    assert (bridge_root / "app.py").exists()
    assert (bridge_root / "core" / "runtime.py").exists()
    assert (bridge_root / "core" / "api" / "bridge_handler.py").exists()
    assert (bridge_root / "packaging" / "linux" / "xuanwu-nearlink-bridge.service").exists()
    assert (bridge_root / "packaging" / "linux" / "xuanwu-nearlink-bridge.spec").exists()
    assert (bridge_root / "packaging" / "windows" / "install-service.ps1").exists()
    assert (bridge_root / "packaging" / "windows" / "service_wrapper.py").exists()
