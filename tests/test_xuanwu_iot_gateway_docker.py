from pathlib import Path


def test_xuanwu_gateway_requirements_include_protocol_dependencies():
    requirements = Path("main/xuanwu-iot-gateway/requirements.txt").read_text(encoding="utf-8")
    assert "sqlalchemy" in requirements.lower()
    assert "psycopg" in requirements.lower()
    assert "pymodbus" in requirements
    assert "opcua" in requirements
    assert "BAC0" in requirements
    assert "paho-mqtt" in requirements


def test_xuanwu_gateway_has_dedicated_dockerfile():
    assert Path("main/xuanwu-iot-gateway/Dockerfile").exists()


def test_xuanwu_gateway_compose_uses_dedicated_dockerfile():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "dockerfile: main/xuanwu-iot-gateway/Dockerfile" in compose


def test_compose_defines_mqtt_broker_service():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "mosquitto:" in compose


def test_compose_passes_postgres_env_to_gateway():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "XUANWU_PG_HOST=" in compose
    assert "XUANWU_PG_DB=" in compose
    assert "XUANWU_IOT_PG_SCHEMA=" in compose
