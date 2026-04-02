from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_xuanwu_portal_dockerfile_exists() -> None:
    dockerfile = REPO_ROOT / "main" / "xuanwu-portal" / "Dockerfile"
    assert dockerfile.exists()
    content = dockerfile.read_text(encoding="utf-8")
    assert "npm run build" in content
    assert "nginx" in content.lower()
    assert "envsubst" in content


def test_compose_includes_xuanwu_portal_service() -> None:
    compose_file = REPO_ROOT / "docker-compose.yml"
    content = compose_file.read_text(encoding="utf-8")
    assert "xuanwu-portal:" in content
    assert '"18081:80"' in content
    assert "XUANWU_PORTAL_CONTROL_SECRET=" in content


def test_nginx_proxies_local_platform_routes() -> None:
    nginx_conf = REPO_ROOT / "main" / "xuanwu-portal" / "nginx.conf.template"
    content = nginx_conf.read_text(encoding="utf-8")
    assert "access_log /var/log/nginx/access.log" in content
    assert "error_log /var/log/nginx/error.log" in content
    for route in ["/control-plane/", "/gateway/", "/runtime/", "/jobs/"]:
        assert route in content
    assert "X-Xuanwu-Control-Secret" in content
    assert "${XUANWU_PORTAL_CONTROL_SECRET}" in content
