from pathlib import Path


def test_management_server_directory_exists():
    root = Path(__file__).resolve().parents[1]

    assert (root / "main" / "xuanwu-management-server" / "app.py").exists()


def test_docker_compose_mentions_management_server_and_xuanwu_address():
    root = Path(__file__).resolve().parents[1]
    compose_text = (
        root / "main" / "xuanwu-device-server" / "docker-compose_all.yml"
    ).read_text(encoding="utf-8")

    assert "xuanwu-management-server" in compose_text
    assert "XUANWU_BASE_URL=http://xuanwu-ai:8000" in compose_text


def test_management_server_readme_mentions_transition_and_xuanwu_address():
    root = Path(__file__).resolve().parents[1]
    readme_text = (
        root / "main" / "xuanwu-management-server" / "README.md"
    ).read_text(encoding="utf-8")

    assert "xuanwu-management-server" in readme_text
    assert "http://xuanwu-ai:8000" in readme_text


def test_device_server_config_mentions_management_server_settings():
    root = Path(__file__).resolve().parents[1]
    config_text = (root / "main" / "xuanwu-device-server" / "config.yaml").read_text(
        encoding="utf-8"
    )

    assert "xuanwu-management-server:" in config_text
    assert "url: http://127.0.0.1:18082" in config_text
