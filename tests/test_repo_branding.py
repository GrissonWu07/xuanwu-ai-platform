from pathlib import Path


def test_runtime_branding_uses_xuanwu_ai():
    root = Path(__file__).resolve().parents[1] / "main" / "xuanwu-device-server"
    config_text = (root / "config.yaml").read_text(encoding="utf-8")
    util_text = (root / "core" / "utils" / "util.py").read_text(encoding="utf-8")

    assert "玄武AI" in config_text
    assert "玄武AI" in util_text
