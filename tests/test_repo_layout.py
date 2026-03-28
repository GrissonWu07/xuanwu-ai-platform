from pathlib import Path


def test_runtime_directory_renamed():
    root = Path(__file__).resolve().parents[1]
    assert (root / "main" / "xuanwu-device-server").exists()
    assert not (root / "main" / "device-server").exists()
