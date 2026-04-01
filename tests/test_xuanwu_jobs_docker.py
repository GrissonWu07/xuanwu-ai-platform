from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_docker_compose_includes_single_xuanwu_jobs_service():
    compose_text = (
        ROOT / "main" / "xuanwu-device-gateway" / "docker-compose_all.yml"
    ).read_text(encoding="utf-8")

    assert "xuanwu-jobs:" in compose_text
    assert "xuanwu-jobs-scheduler:" not in compose_text
    assert "xuanwu-jobs-worker:" not in compose_text
    assert "redis:" not in compose_text
    assert "XUANWU_MANAGEMENT_SERVER_URL=http://xuanwu-management-server:18082" in compose_text


def test_docker_setup_bootstraps_xuanwu_jobs_stack():
    setup_text = (ROOT / "docker-setup.sh").read_text(encoding="utf-8")

    assert "xuanwu-jobs" in setup_text
    assert "redis" not in setup_text
    assert "docker compose -f \"$COMPOSE_PATH\" up -d" in setup_text


def test_jobs_docs_explain_lightweight_jobs_service():
    jobs_readme_text = (ROOT / "main" / "xuanwu-jobs" / "README.md").read_text(
        encoding="utf-8"
    )
    main_readme_text = (ROOT / "main" / "README_en.md").read_text(encoding="utf-8")

    assert "xuanwu-jobs-worker" not in jobs_readme_text
    assert "redis" not in jobs_readme_text.lower()
    assert "scheduler-dispatcher" in jobs_readme_text
    assert "xuanwu-jobs" in main_readme_text
    assert "scheduler-dispatcher" in main_readme_text
    assert "xuanwu-device-gateway" in main_readme_text
    assert "xuanwu-iot-gateway" in main_readme_text
