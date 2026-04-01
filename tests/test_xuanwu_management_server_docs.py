from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_management_server_directory_exists():
    assert (ROOT / "main" / "xuanwu-management-server" / "app.py").exists()


def test_docker_compose_is_python_primary_only():
    compose_text = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "xuanwu-management-server" in compose_text
    assert "XUANWU_BASE_URL=${XUANWU_BASE_URL:-http://xuanwu-ai:8000}" in compose_text
    assert "xuanwu-device-gateway-web" not in compose_text
    assert "xuanwu-device-gateway-db" not in compose_text
    assert "xuanwu-device-gateway-redis" not in compose_text
    assert "legacy-java" not in compose_text


def test_device_server_config_mentions_management_server_only():
    config_text = (ROOT / "main" / "xuanwu-device-gateway" / "config.yaml").read_text(
        encoding="utf-8"
    )

    assert "xuanwu-management-server:" in config_text
    assert "url: http://127.0.0.1:18082" in config_text
    assert "manager-api:" not in config_text


def test_manager_api_template_is_removed():
    assert not (ROOT / "main" / "xuanwu-device-gateway" / "config_from_api.yaml").exists()


def test_docker_setup_bootstraps_python_management_path_only():
    setup_text = (ROOT / "docker-setup.sh").read_text(encoding="utf-8")

    assert "xuanwu-management-server" in setup_text
    assert "config_from_api.yaml" not in setup_text
    assert "manager-api" not in setup_text
    assert "manager-web" not in setup_text


def test_xuanwu_upstream_gap_requirements_doc_exists():
    spec_path = (
        ROOT
        / "docs"
        / "superpowers"
        / "specs"
        / "2026-03-28-xuanwu-upstream-gap-requirements.md"
    )
    assert spec_path.exists()
    spec_text = spec_path.read_text(encoding="utf-8")

    assert "XuanWu" in spec_text
    assert "/xuanwu/v1/admin/agents" in spec_text
    assert "/xuanwu/v1/admin/model-providers" in spec_text
    assert "/xuanwu/v1/admin/models" in spec_text


def test_docs_describe_postgres_first_persistence():
    for relative_path in (
        "docs/quick-start.md",
        "docs/Deployment.md",
        "docs/current-platform-capabilities.md",
        "docs/current-api-surfaces.md",
        "docs/platform-delivery-overview.md",
    ):
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert "PostgreSQL" in text
        assert "xw_mgmt" in text
        assert "xw_iot" in text
        assert "deploy/postgres" in text
