from pathlib import Path


def test_xuanwu_gateway_requirements_include_protocol_dependencies():
    requirements = Path("main/xuanwu-gateway/requirements.txt").read_text(encoding="utf-8")
    assert "pymodbus" in requirements
    assert "opcua" in requirements
    assert "BAC0" in requirements
    assert "paho-mqtt" in requirements


def test_xuanwu_gateway_has_dedicated_dockerfile():
    assert Path("main/xuanwu-gateway/Dockerfile").exists()


def test_xuanwu_gateway_compose_uses_dedicated_dockerfile():
    compose = Path("main/xuanwu-device-server/docker-compose_all.yml").read_text(encoding="utf-8")
    assert "dockerfile: main/xuanwu-gateway/Dockerfile" in compose


def test_compose_defines_mqtt_broker_service():
    compose = Path("main/xuanwu-device-server/docker-compose_all.yml").read_text(encoding="utf-8")
    assert "mosquitto:" in compose
