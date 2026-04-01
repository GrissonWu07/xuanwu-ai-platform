# XuanWu Gateway Gap Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the highest-value remaining local `xuanwu-iot-gateway` gaps by strengthening MQTT, Home Assistant, Modbus, and deployment packaging without depending on upstream `XuanWu`.

**Architecture:** Keep the existing unified gateway contract and registry structure, then deepen selected adapters behind the same `GatewayHandler` surfaces. The first closure pass focuses on realistic local improvements that stay inside this repository: broker-aware MQTT ingestion, Home Assistant state reads, expanded Modbus read coverage, and formalized gateway dependency packaging.

**Tech Stack:** Python 3.11, aiohttp, urllib/httpx-style HTTP clients, paho-mqtt, pymodbus, opcua, BAC0, pytest

---

### Task 1: Update gateway specs and implementation ledger

**Files:**
- Modify: `docs/superpowers/specs/2026-03-31-xuanwu-iot-gateway-adapter-completion-spec.md`
- Modify: `docs/superpowers/specs/2026-03-31-spec-completion-status.md`

- [ ] **Step 1: Document the remaining MQTT, Home Assistant, industrial, and packaging gaps**

Add explicit sections describing:

- MQTT still lacks broker-backed subscription semantics
- Home Assistant still lacks state-read support
- Modbus still lacks the full baseline read set
- gateway packaging still lacks formal dependency declarations

- [ ] **Step 2: Run a quick spec sanity read**

Run: `Get-Content docs\\superpowers\\specs\\2026-03-31-xuanwu-iot-gateway-adapter-completion-spec.md -Tail 140`
Expected: the file now includes the new remaining-gap sections

### Task 2: Write failing tests for MQTT broker-backed ingestion support

**Files:**
- Modify: `main/xuanwu-iot-gateway/tests/test_mqtt_adapter.py`

- [ ] **Step 1: Write the failing test**

Add:

```python
def test_mqtt_adapter_normalizes_broker_message_into_gateway_ingest_payload():
    module = _load_module("xuanwu_gateway_mqtt_adapter_norm", "mqtt_adapter.py")
    adapter = module.MqttAdapter()

    result = adapter.normalize_broker_message(
        {
            "device_id": "sensor-mqtt-001",
            "gateway_id": "gateway-mqtt-001",
            "topic": "factory/line-1/temp",
            "observed_at": "2026-03-31T10:00:00Z",
            "telemetry": {"temperature": 24.6, "humidity": 53.1},
        }
    )

    assert result["status"] == "accepted"
    assert result["telemetry"][0]["metrics"]["temperature"] == 24.6
    assert result["events"][0]["payload"]["topic"] == "factory/line-1/temp"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest main/xuanwu-iot-gateway/tests/test_mqtt_adapter.py -q`
Expected: FAIL because `normalize_broker_message` does not exist yet

### Task 3: Write failing tests for Home Assistant state read support

**Files:**
- Modify: `main/xuanwu-iot-gateway/tests/test_home_assistant_adapter.py`

- [ ] **Step 1: Write the failing test**

Add:

```python
def test_home_assistant_adapter_reads_entity_state():
    module = _load_module("xuanwu_gateway_home_assistant_adapter_state", "home_assistant_adapter.py")

    class FakeTransport:
        def __init__(self):
            self.calls = []

        def request(self, **kwargs):
            self.calls.append(kwargs)
            return {"status": "ok", "status_code": 200, "body": {"state": "on", "attributes": {"brightness": 80}}}

    adapter = module.HomeAssistantAdapter(transport=FakeTransport())
    result = adapter.dispatch(
        {
            "request_id": "req-ha-read-001",
            "gateway_id": "gateway-ha-001",
            "adapter_type": "home_assistant",
            "device_id": "ha-light-001",
            "capability_code": "home_assistant.state",
            "command_name": "read_state",
            "route": {
                "base_url": "http://ha.local:8123",
                "token": "secret-token",
                "entity_id": "light.living_room",
            },
        }
    )

    assert result["status"] == "succeeded"
    assert result["result"]["protocol_response"]["body"]["state"] == "on"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest main/xuanwu-iot-gateway/tests/test_home_assistant_adapter.py -q`
Expected: FAIL because `read_state` is not translated yet

### Task 4: Write failing tests for expanded Modbus reads

**Files:**
- Modify: `main/xuanwu-iot-gateway/tests/test_industrial_adapters.py`

- [ ] **Step 1: Write the failing tests**

Add:

```python
def test_modbus_tcp_adapter_reads_coils():
    module = _load_module("xuanwu_gateway_modbus_adapter_coils", "modbus_tcp_adapter.py")
    transport = FakeTransport({"status": "ok", "values": [True, False, True]})
    adapter = module.ModbusTcpAdapter(transport=transport)

    result = adapter.dispatch(
        {
            "request_id": "req-modbus-coils-001",
            "gateway_id": "gateway-modbus-001",
            "adapter_type": "modbus_tcp",
            "device_id": "plc-001",
            "capability_code": "industrial.coil.read",
            "command_name": "read_coils",
            "route": {"host": "10.0.0.20", "address": 1, "quantity": 3},
        }
    )

    assert result["status"] == "succeeded"
    assert transport.calls[0]["function"] == "read_coils"
    assert result["result"]["protocol_response"]["values"] == [True, False, True]
```

Repeat with:

- `read_discrete_inputs`
- `read_input_registers`

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest main/xuanwu-iot-gateway/tests/test_industrial_adapters.py -q`
Expected: FAIL because the new functions are unsupported

### Task 5: Implement MQTT broker-message normalization minimally

**Files:**
- Modify: `main/xuanwu-iot-gateway/core/adapters/mqtt_adapter.py`

- [ ] **Step 1: Write minimal implementation**

Add:

```python
    def normalize_broker_message(self, payload: dict) -> dict:
        return {
            "status": "accepted",
            "telemetry": [{
                "telemetry_id": payload.get("telemetry_id") or f"telemetry-{payload.get('device_id')}",
                "device_id": payload.get("device_id"),
                "gateway_id": payload.get("gateway_id"),
                "capability_code": payload.get("capability_code") or "sensor.mqtt",
                "observed_at": payload.get("observed_at"),
                "metrics": dict(payload.get("telemetry") or {}),
            }],
            "events": [{
                "event_id": payload.get("event_id") or f"event-{payload.get('device_id')}",
                "device_id": payload.get("device_id"),
                "gateway_id": payload.get("gateway_id"),
                "event_type": "telemetry.reported",
                "severity": "info",
                "occurred_at": payload.get("observed_at"),
                "payload": {
                    "topic": payload.get("topic"),
                    **dict(payload.get("telemetry") or {}),
                },
            }],
        }
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `python -m pytest main/xuanwu-iot-gateway/tests/test_mqtt_adapter.py -q`
Expected: PASS

### Task 6: Implement Home Assistant state reads minimally

**Files:**
- Modify: `main/xuanwu-iot-gateway/core/adapters/home_assistant_adapter.py`

- [ ] **Step 1: Write minimal implementation**

Support `read_state` by translating to:

```python
{
    "url": f"{str(route.get('base_url') or '').rstrip('/')}/api/states/{route.get('entity_id')}",
    "method": "GET",
    "headers": {"Authorization": f"Bearer {route.get('token')}"},
    "timeout_ms": route.get("timeout_ms", 5000),
}
```

and allow `entity_id` without service metadata when `command_name == "read_state"`.

- [ ] **Step 2: Run tests to verify they pass**

Run: `python -m pytest main/xuanwu-iot-gateway/tests/test_home_assistant_adapter.py -q`
Expected: PASS

### Task 7: Implement expanded Modbus reads minimally

**Files:**
- Modify: `main/xuanwu-iot-gateway/core/adapters/modbus_tcp_adapter.py`

- [ ] **Step 1: Write minimal implementation**

Add support for:

```python
if function == "read_coils":
    response = client.read_coils(kwargs["address"], count=kwargs["quantity"], slave=kwargs["unit_id"])
    values = list(response.bits or [])[: kwargs["quantity"]] if not response.isError() else None
    return {"status": "ok" if not response.isError() else "failed", "values": values}

if function == "read_discrete_inputs":
    response = client.read_discrete_inputs(kwargs["address"], count=kwargs["quantity"], slave=kwargs["unit_id"])
    values = list(response.bits or [])[: kwargs["quantity"]] if not response.isError() else None
    return {"status": "ok" if not response.isError() else "failed", "values": values}

if function == "read_input_registers":
    response = client.read_input_registers(kwargs["address"], count=kwargs["quantity"], slave=kwargs["unit_id"])
    values = list(response.registers or []) if not response.isError() else None
    return {"status": "ok" if not response.isError() else "failed", "values": values}
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `python -m pytest main/xuanwu-iot-gateway/tests/test_industrial_adapters.py -q`
Expected: PASS

### Task 8: Formalize gateway dependencies and Docker packaging

**Files:**
- Create: `main/xuanwu-iot-gateway/requirements.txt`
- Create: `main/xuanwu-iot-gateway/Dockerfile`
- Modify: `main/xuanwu-device-gateway/docker-compose_all.yml`
- Create: `tests/test_xuanwu_iot_gateway_docker.py`

- [ ] **Step 1: Write the failing test**

Create:

```python
from pathlib import Path


def test_xuanwu_gateway_requirements_include_protocol_dependencies():
    requirements = Path("main/xuanwu-iot-gateway/requirements.txt").read_text(encoding="utf-8")
    assert "pymodbus" in requirements
    assert "opcua" in requirements
    assert "BAC0" in requirements
    assert "paho-mqtt" in requirements


def test_xuanwu_gateway_has_dedicated_dockerfile():
    assert Path("main/xuanwu-iot-gateway/Dockerfile").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_xuanwu_iot_gateway_docker.py -q`
Expected: FAIL because the files do not exist yet

- [ ] **Step 3: Write minimal implementation**

Create `main/xuanwu-iot-gateway/requirements.txt`:

```txt
aiohttp
httpx
pymodbus
opcua
BAC0
paho-mqtt
```

Create `main/xuanwu-iot-gateway/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /opt/xuanwu-iot-gateway

COPY main/xuanwu-iot-gateway/requirements.txt /tmp/xuanwu-iot-gateway-requirements.txt
RUN pip install --no-cache-dir -r /tmp/xuanwu-iot-gateway-requirements.txt

COPY main/xuanwu-iot-gateway /opt/xuanwu-iot-gateway

CMD ["python", "app.py"]
```

Update compose to use the dedicated Dockerfile instead of inline `pip install`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_xuanwu_iot_gateway_docker.py -q`
Expected: PASS

### Task 9: Run focused verification and regression

**Files:**
- Test: `main/xuanwu-iot-gateway/tests/test_mqtt_adapter.py`
- Test: `main/xuanwu-iot-gateway/tests/test_home_assistant_adapter.py`
- Test: `main/xuanwu-iot-gateway/tests/test_industrial_adapters.py`
- Test: `main/xuanwu-iot-gateway/tests/test_dispatch.py`
- Test: `main/xuanwu-iot-gateway/tests/test_registry.py`
- Test: `tests/test_xuanwu_iot_gateway_docker.py`

- [ ] **Step 1: Run focused gateway tests**

Run:

```bash
python -m pytest main/xuanwu-iot-gateway/tests/test_mqtt_adapter.py main/xuanwu-iot-gateway/tests/test_home_assistant_adapter.py main/xuanwu-iot-gateway/tests/test_industrial_adapters.py tests/test_xuanwu_iot_gateway_docker.py -q
```

Expected: all pass

- [ ] **Step 2: Run broader gateway regression**

Run:

```bash
python -m pytest main/xuanwu-iot-gateway/tests main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py -q
```

Expected: all pass

- [ ] **Step 3: Run Python compile verification**

Run:

```bash
python -m py_compile main/xuanwu-iot-gateway/app.py main/xuanwu-iot-gateway/core/http_server.py main/xuanwu-iot-gateway/core/api/gateway_handler.py main/xuanwu-iot-gateway/core/adapters/mqtt_adapter.py main/xuanwu-iot-gateway/core/adapters/home_assistant_adapter.py main/xuanwu-iot-gateway/core/adapters/modbus_tcp_adapter.py
```

Expected: no output, exit code 0

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-03-31-xuanwu-iot-gateway-adapter-completion-spec.md docs/superpowers/specs/2026-03-31-spec-completion-status.md docs/superpowers/plans/2026-03-31-xuanwu-iot-gateway-gap-closure-plan.md main/xuanwu-iot-gateway/core/adapters/mqtt_adapter.py main/xuanwu-iot-gateway/core/adapters/home_assistant_adapter.py main/xuanwu-iot-gateway/core/adapters/modbus_tcp_adapter.py main/xuanwu-iot-gateway/tests/test_mqtt_adapter.py main/xuanwu-iot-gateway/tests/test_home_assistant_adapter.py main/xuanwu-iot-gateway/tests/test_industrial_adapters.py main/xuanwu-iot-gateway/requirements.txt main/xuanwu-iot-gateway/Dockerfile main/xuanwu-device-gateway/docker-compose_all.yml tests/test_xuanwu_iot_gateway_docker.py
git commit -m "feat: close gateway adapter capability gaps"
```
