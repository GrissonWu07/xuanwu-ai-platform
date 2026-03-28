from pathlib import Path


def test_runtime_http_server_no_longer_hosts_control_plane_routes():
    http_server_path = (
        Path(__file__).resolve().parents[1] / "core" / "http_server.py"
    )
    content = http_server_path.read_text(encoding="utf-8")

    assert "/control-plane/v1/" not in content
