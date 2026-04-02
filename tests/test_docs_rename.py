from pathlib import Path


def test_root_docs_use_xuanwu_device_gateway():
    root = Path(__file__).resolve().parents[1]
    readme_text = (root / "README.md").read_text(encoding="utf-8")
    readme_zh_text = (root / "README_zh.md").read_text(encoding="utf-8")

    assert "xuanwu-device-gateway" in readme_text
    assert "xuanwu-iot-gateway" in readme_text
    assert "# XuanWu AI Device Platform" in readme_text
    assert "/xuanwu/ota/" in readme_text
    assert "/xuanwu/v1/" in readme_text
    assert "玄武AI" in readme_zh_text
    assert "[简体中文](./README_zh.md)" in readme_text
    assert "[English](./README.md)" in readme_zh_text
