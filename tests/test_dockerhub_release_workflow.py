from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dockerhub_release_workflow_exists() -> None:
    workflow = ROOT / ".github" / "workflows" / "dockerhub-release.yml"
    assert workflow.exists()


def test_dockerhub_release_workflow_contract() -> None:
    workflow = ROOT / ".github" / "workflows" / "dockerhub-release.yml"
    text = workflow.read_text(encoding="utf-8")

    assert "docker/login-action" in text
    assert "DOCKERHUB_NAMESPACE: xuanwu" in text
    assert "DOCKERHUB_USERNAME" in text
    assert "DOCKERHUB_TOKEN" in text
    assert "workflow_dispatch:" in text
    assert "push:" in text
    assert "main" in text
    assert 'v*.*.*' in text or '"v*.*.*"' in text
    assert "images: ${{ env.DOCKERHUB_NAMESPACE }}/${{ matrix.image }}" in text
    assert "xuanwu-portal" in text
    assert "xuanwu-device-gateway" in text
    assert "xuanwu-management-server" in text
    assert "xuanwu-iot-gateway" in text
    assert "xuanwu-jobs" in text


def test_release_dockerfiles_exist() -> None:
    root = ROOT / "main"
    assert (root / "xuanwu-portal" / "Dockerfile").exists()
    assert (root / "xuanwu-device-gateway" / "Dockerfile").exists()
    assert (root / "xuanwu-management-server" / "Dockerfile").exists()
    assert (root / "xuanwu-iot-gateway" / "Dockerfile").exists()
    assert (root / "xuanwu-jobs" / "Dockerfile").exists()
