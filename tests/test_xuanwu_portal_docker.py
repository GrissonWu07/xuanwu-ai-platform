from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_xuanwu_portal_dockerfile_exists() -> None:
    dockerfile = REPO_ROOT / "main" / "xuanwu-portal" / "Dockerfile"
    assert dockerfile.exists()
    content = dockerfile.read_text(encoding="utf-8")
    assert "npm run build" in content
    assert "nginx" in content.lower()


def test_compose_includes_xuanwu_portal_service() -> None:
    compose_file = REPO_ROOT / "main" / "xuanwu-device-server" / "docker-compose_all.yml"
    content = compose_file.read_text(encoding="utf-8")
    assert "xuanwu-portal:" in content
    assert '"18081:80"' in content


def test_nginx_proxies_local_platform_routes() -> None:
    nginx_conf = REPO_ROOT / "main" / "xuanwu-portal" / "nginx.conf"
    content = nginx_conf.read_text(encoding="utf-8")
    for route in ["/control-plane/", "/gateway/", "/runtime/", "/jobs/"]:
        assert route in content
