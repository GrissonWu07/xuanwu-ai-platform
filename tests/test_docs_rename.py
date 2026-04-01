from pathlib import Path


def test_root_docs_use_xuanwu_device_gateway():
    root = Path(__file__).resolve().parents[1]
    readme_text = (root / "README.md").read_text(encoding="utf-8")

    assert "xuanwu-device-gateway" in readme_text
    assert "xuanwu-iot-gateway" in readme_text
    assert "玄武AI" in readme_text
    assert "/xuanwu/ota/" in readme_text
    assert "/xuanwu/v1/" in readme_text
