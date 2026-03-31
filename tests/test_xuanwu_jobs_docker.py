from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_docker_compose_includes_xuanwu_jobs_and_redis():
    compose_text = (
        ROOT / "main" / "xuanwu-device-server" / "docker-compose_all.yml"
    ).read_text(encoding="utf-8")

    assert "redis:" in compose_text
    assert "xuanwu-jobs-scheduler:" in compose_text
    assert "xuanwu-jobs-platform-worker:" in compose_text
    assert "XUANWU_JOBS_REDIS_URL=redis://redis:6379/0" in compose_text
    assert "XUANWU_MANAGEMENT_SERVER_URL=http://xuanwu-management-server:18082" in compose_text


def test_docker_setup_bootstraps_xuanwu_jobs_stack():
    setup_text = (ROOT / "docker-setup.sh").read_text(encoding="utf-8")

    assert "xuanwu-jobs" in setup_text
    assert "redis" in setup_text
    assert "docker compose -f \"$COMPOSE_PATH\" up -d" in setup_text


def test_jobs_docs_explain_worker_scaling_in_docker():
    jobs_readme_text = (ROOT / "main" / "xuanwu-jobs" / "README.md").read_text(
        encoding="utf-8"
    )
    main_readme_text = (ROOT / "main" / "README_en.md").read_text(encoding="utf-8")

    assert "xuanwu-jobs-platform-worker" in jobs_readme_text
    assert "docker compose up -d --scale xuanwu-jobs-platform-worker=3" in jobs_readme_text
    assert "xuanwu-jobs" in main_readme_text
    assert "worker replicas" in main_readme_text
