from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_root_compose_exists_and_hosts_platform_stack() -> None:
    compose_file = ROOT / "docker-compose.yml"
    assert compose_file.exists()

    content = compose_file.read_text(encoding="utf-8")
    for service_name in [
        "xuanwu-portal:",
        "xuanwu-management-server:",
        "xuanwu-jobs:",
        "xuanwu-device-gateway:",
        "xuanwu-iot-gateway:",
        "mosquitto:",
    ]:
        assert service_name in content


def test_root_compose_uses_root_deploy_mounts() -> None:
    compose_file = ROOT / "docker-compose.yml"
    content = compose_file.read_text(encoding="utf-8")

    assert "./deploy/data/device-gateway:/opt/xuanwu-device-gateway/data" in content
    assert (
        "./deploy/models/SenseVoiceSmall/model.pt:"
        "/opt/xuanwu-device-gateway/models/SenseVoiceSmall/model.pt"
    ) in content


def test_root_setup_script_bootstraps_repo_root() -> None:
    setup_script = (ROOT / "docker-setup.sh").read_text(encoding="utf-8")

    assert "/opt/xuanwu-ai-platform" in setup_script
    assert 'COMPOSE_PATH="$PROJECT_ROOT/docker-compose.yml"' in setup_script
    assert 'DATA_DIR="$PROJECT_ROOT/deploy/data/device-gateway"' in setup_script
    assert 'MODEL_DIR="$PROJECT_ROOT/deploy/models/SenseVoiceSmall"' in setup_script
    assert "git clone https://github.com/GrissonWu07/xuanwu-ai-platform.git" in setup_script
    assert 'ENV_PATH="$PROJECT_ROOT/.env"' in setup_script


def test_root_env_example_exposes_xuanwu_endpoint() -> None:
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")

    assert "XUANWU_BASE_URL=http://xuanwu-ai:8000" in env_example
    assert "XUANWU_CONTROL_PLANE_SECRET=" in env_example


def test_gitignore_covers_root_deploy_runtime_artifacts() -> None:
    gitignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "deploy/data/" in gitignore_text
    assert "!deploy/data/device-gateway/" in gitignore_text
    assert "!deploy/data/device-gateway/.gitkeep" in gitignore_text
    assert "deploy/models/SenseVoiceSmall/model.pt" in gitignore_text
