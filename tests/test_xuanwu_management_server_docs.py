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
    assert "默认主管理宿主" in compose_text
    assert "兼容模块" in compose_text
    assert "profiles:" in compose_text
    assert "legacy-java" in compose_text


def test_management_server_readme_mentions_transition_and_xuanwu_address():
    root = Path(__file__).resolve().parents[1]
    readme_text = (
        root / "main" / "xuanwu-management-server" / "README.md"
    ).read_text(encoding="utf-8")

    assert "xuanwu-management-server" in readme_text
    assert "http://xuanwu-ai:8000" in readme_text
    assert "/control-plane/v1/xuanwu/agents/{agent_id}" in readme_text


def test_device_server_config_mentions_management_server_settings():
    root = Path(__file__).resolve().parents[1]
    config_text = (root / "main" / "xuanwu-device-server" / "config.yaml").read_text(
        encoding="utf-8"
    )

    assert "xuanwu-management-server:" in config_text
    assert "url: http://127.0.0.1:18082" in config_text


def test_manager_api_compatibility_template_requires_explicit_enable():
    root = Path(__file__).resolve().parents[1]
    template_text = (
        root / "main" / "xuanwu-device-server" / "config_from_api.yaml"
    ).read_text(encoding="utf-8")

    assert "enabled: true" in template_text
    assert "兼容模式" in template_text


def test_docker_setup_explicitly_enables_manager_api_compatibility_mode():
    root = Path(__file__).resolve().parents[1]
    setup_text = (root / "docker-setup.sh").read_text(encoding="utf-8")

    assert "config['manager-api']" in setup_text
    assert "\"enabled\": True" in setup_text or "'enabled': True" in setup_text


def test_refactor_doc_mentions_management_server_transition():
    root = Path(__file__).resolve().parents[1]
    doc_text = (
        root
        / "docs"
        / "python-first-refactor"
        / "fallback-config-center-and-java-sunset.md"
    ).read_text(encoding="utf-8")

    assert "xuanwu-management-server" in doc_text
    assert "http://xuanwu-ai:8000" in doc_text


def test_deployment_doc_prefers_management_server_over_legacy_java_path():
    root = Path(__file__).resolve().parents[1]
    doc_text = (root / "docs" / "Deployment_all.md").read_text(encoding="utf-8")

    assert "xuanwu-management-server" in doc_text
    assert "默认主管理宿主" in doc_text
    assert "legacy 兼容模式" in doc_text
    assert "--profile legacy-java" in doc_text


def test_dev_ops_doc_mentions_management_server_as_primary_path():
    root = Path(__file__).resolve().parents[1]
    doc_text = (root / "docs" / "dev-ops-integration.md").read_text(encoding="utf-8")

    assert "xuanwu-management-server" in doc_text
    assert "默认主路径" in doc_text


def test_main_readmes_include_management_server_migration_note():
    root = Path(__file__).resolve().parents[1]
    zh_text = (root / "main" / "README.md").read_text(encoding="utf-8")
    en_text = (root / "main" / "README_en.md").read_text(encoding="utf-8")

    assert "xuanwu-management-server" in zh_text
    assert "http://xuanwu-ai:8000" in zh_text
    assert "默认主管理宿主" in zh_text
    assert "管理配置主线" in zh_text
    assert "xuanwu-management-server -> XuanWu" in zh_text
    assert "Java 兼容参考实现" in zh_text
    assert "xuanwu-management-server" in en_text
    assert "http://xuanwu-ai:8000" in en_text
    assert "default primary management host" in en_text
    assert "Management Configuration Main Line" in en_text
    assert "xuanwu-management-server -> XuanWu" in en_text
    assert "Java compatibility reference implementation" in en_text


def test_docker_setup_mentions_legacy_manager_api_compatibility_mode():
    root = Path(__file__).resolve().parents[1]
    setup_text = (root / "docker-setup.sh").read_text(encoding="utf-8")

    assert "legacy 兼容模式" in setup_text
    assert "manager-api" in setup_text


def test_main_readmes_reframe_management_flow_and_deployment_to_python_primary_path():
    root = Path(__file__).resolve().parents[1]
    zh_text = (root / "main" / "README.md").read_text(encoding="utf-8")
    en_text = (root / "main" / "README_en.md").read_text(encoding="utf-8")

    assert "管理与配置流程 (`xuanwu-management-server` <-> `XuanWu` <-> `xuanwu-device-server`)" in zh_text
    assert "动态远程配置" in zh_text
    assert "全模块安装（默认主路径）" in zh_text
    assert "legacy-java profile" in zh_text

    assert "Management and Configuration Flow (`xuanwu-management-server` <-> `XuanWu` <-> `xuanwu-device-server`)" in en_text
    assert "Dynamic Remote Configuration" in en_text
    assert "Full Module Installation (Default Primary Path)" in en_text
    assert "legacy-java profile" in en_text
