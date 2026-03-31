# XuanWu Gateway Adapter Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `xuanwu-gateway` from a skeleton registry into a protocol-backed adapter layer for the current HTTP, MQTT, Home Assistant, HTTP push, MQTT ingest, and industrial adapter families.

**Architecture:** Keep `xuanwu-gateway` as the protocol execution layer, with adapters behind a common registry and unified northbound HTTP API. Use explicit adapter configuration validation, protocol-specific transport helpers, and deterministic fake transports in tests so behavior is verifiable without requiring every external broker or industrial controller in the local suite.

**Tech Stack:** Python, aiohttp, socket/urllib stdlib, optional protocol libraries behind guarded imports, pytest

---

## File Structure

- Create:
  - `main/xuanwu-gateway/core/adapters/exceptions.py`
  - `main/xuanwu-gateway/core/adapters/sensor_http_push_adapter.py`
  - `main/xuanwu-gateway/core/adapters/sensor_mqtt_adapter.py`
  - `main/xuanwu-gateway/core/adapters/modbus_tcp_adapter.py`
  - `main/xuanwu-gateway/core/adapters/opc_ua_adapter.py`
  - `main/xuanwu-gateway/core/adapters/bacnet_ip_adapter.py`
  - `main/xuanwu-gateway/core/adapters/can_gateway_adapter.py`
  - `main/xuanwu-gateway/core/adapters/bluetooth_adapter.py`
  - `main/xuanwu-gateway/core/adapters/nearlink_adapter.py`
  - `main/xuanwu-gateway/tests/test_http_adapter.py`
  - `main/xuanwu-gateway/tests/test_home_assistant_adapter.py`
  - `main/xuanwu-gateway/tests/test_mqtt_adapter.py`
  - `main/xuanwu-gateway/tests/test_sensor_ingest.py`
  - `main/xuanwu-gateway/tests/test_industrial_adapters.py`
  - `main/xuanwu-gateway/tests/test_wireless_adapters.py`
- Modify:
  - `main/xuanwu-gateway/core/adapters/base.py`
  - `main/xuanwu-gateway/core/adapters/http_adapter.py`
  - `main/xuanwu-gateway/core/adapters/home_assistant_adapter.py`
  - `main/xuanwu-gateway/core/adapters/mqtt_adapter.py`
  - `main/xuanwu-gateway/core/api/gateway_handler.py`
  - `main/xuanwu-gateway/core/clients/management_client.py`
  - `main/xuanwu-gateway/core/contracts/models.py`
  - `main/xuanwu-gateway/core/registry/adapter_registry.py`
  - `main/xuanwu-gateway/tests/test_dispatch.py`
  - `main/xuanwu-gateway/tests/test_registry.py`
  - `main/xuanwu-gateway/tests/test_bootstrap.py`

## Task 1: Establish adapter error and validation model

**Files:**
- Create: `main/xuanwu-gateway/core/adapters/exceptions.py`
- Modify: `main/xuanwu-gateway/core/adapters/base.py`
- Test: `main/xuanwu-gateway/tests/test_registry.py`

- [ ] **Step 1: Write the failing tests**

Add tests that assert adapters now describe supported capabilities and that validation failures return normalized gateway errors instead of generic acceptance payloads.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest main/xuanwu-gateway/tests/test_registry.py -q`
Expected: FAIL because adapters do not expose the richer metadata/validation behavior yet.

- [ ] **Step 3: Write minimal implementation**

Add adapter exceptions and a richer base adapter with:
- `validate_command()`
- `validate_ingest_payload()`
- `dispatch()`
- `describe()` including `supports_ingest` and `supported_capabilities`

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest main/xuanwu-gateway/tests/test_registry.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-gateway/core/adapters/exceptions.py main/xuanwu-gateway/core/adapters/base.py main/xuanwu-gateway/tests/test_registry.py
git commit -m "feat: add gateway adapter validation model"
```

## Task 2: Implement real HTTP actuator adapter

**Files:**
- Modify: `main/xuanwu-gateway/core/adapters/http_adapter.py`
- Modify: `main/xuanwu-gateway/core/api/gateway_handler.py`
- Test: `main/xuanwu-gateway/tests/test_http_adapter.py`
- Test: `main/xuanwu-gateway/tests/test_dispatch.py`

- [ ] **Step 1: Write the failing tests**

Add tests that use a valid HTTP actuator command payload with:
- target URL
- method
- headers
- body template
- timeout

Assert:
- request mapping is correct
- success normalizes to `CapabilityCommandResult`
- HTTP failure normalizes to adapter error status

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest main/xuanwu-gateway/tests/test_http_adapter.py main/xuanwu-gateway/tests/test_dispatch.py -q`
Expected: FAIL because the current adapter only returns dry-run acceptance.

- [ ] **Step 3: Write minimal implementation**

Implement:
- command config validation
- pluggable HTTP transport
- response normalization
- optional state-follow-up passthrough fields in result payload

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest main/xuanwu-gateway/tests/test_http_adapter.py main/xuanwu-gateway/tests/test_dispatch.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-gateway/core/adapters/http_adapter.py main/xuanwu-gateway/core/api/gateway_handler.py main/xuanwu-gateway/tests/test_http_adapter.py main/xuanwu-gateway/tests/test_dispatch.py
git commit -m "feat: implement gateway http adapter"
```

## Task 3: Implement Home Assistant service-call adapter

**Files:**
- Modify: `main/xuanwu-gateway/core/adapters/home_assistant_adapter.py`
- Test: `main/xuanwu-gateway/tests/test_home_assistant_adapter.py`

- [ ] **Step 1: Write the failing tests**

Add tests using valid Home Assistant-shaped data:
- base URL
- token
- service domain
- service name
- entity id
- service data

Assert:
- correct REST endpoint construction
- authorization header usage
- normalized success/failure result

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest main/xuanwu-gateway/tests/test_home_assistant_adapter.py -q`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement the adapter as a specialized HTTP executor with Home Assistant-specific request shaping.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest main/xuanwu-gateway/tests/test_home_assistant_adapter.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-gateway/core/adapters/home_assistant_adapter.py main/xuanwu-gateway/tests/test_home_assistant_adapter.py
git commit -m "feat: implement gateway home assistant adapter"
```

## Task 4: Implement MQTT actuator adapter

**Files:**
- Modify: `main/xuanwu-gateway/core/adapters/mqtt_adapter.py`
- Test: `main/xuanwu-gateway/tests/test_mqtt_adapter.py`

- [ ] **Step 1: Write the failing tests**

Add tests with valid MQTT command payloads containing:
- broker host/port
- publish topic
- qos
- retain
- payload template

Assert:
- publish request is shaped correctly
- command result normalizes publish metadata
- failures normalize cleanly

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest main/xuanwu-gateway/tests/test_mqtt_adapter.py -q`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement a pluggable MQTT publish transport with optional library-backed runtime and deterministic fake transport in tests.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest main/xuanwu-gateway/tests/test_mqtt_adapter.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-gateway/core/adapters/mqtt_adapter.py main/xuanwu-gateway/tests/test_mqtt_adapter.py
git commit -m "feat: implement gateway mqtt adapter"
```

## Task 5: Implement sensor ingest adapters

**Files:**
- Create: `main/xuanwu-gateway/core/adapters/sensor_http_push_adapter.py`
- Create: `main/xuanwu-gateway/core/adapters/sensor_mqtt_adapter.py`
- Modify: `main/xuanwu-gateway/core/api/gateway_handler.py`
- Modify: `main/xuanwu-gateway/core/clients/management_client.py`
- Test: `main/xuanwu-gateway/tests/test_sensor_ingest.py`
- Test: `main/xuanwu-gateway/tests/test_bootstrap.py`

- [ ] **Step 1: Write the failing tests**

Add tests for:
- HTTP push telemetry ingest
- MQTT telemetry ingest bridge payload
- event normalization
- callback posting to management client

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest main/xuanwu-gateway/tests/test_sensor_ingest.py main/xuanwu-gateway/tests/test_bootstrap.py -q`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Add:
- sensor adapters
- ingest endpoints in gateway handler
- management callback methods for telemetry and events

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest main/xuanwu-gateway/tests/test_sensor_ingest.py main/xuanwu-gateway/tests/test_bootstrap.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-gateway/core/adapters/sensor_http_push_adapter.py main/xuanwu-gateway/core/adapters/sensor_mqtt_adapter.py main/xuanwu-gateway/core/api/gateway_handler.py main/xuanwu-gateway/core/clients/management_client.py main/xuanwu-gateway/tests/test_sensor_ingest.py main/xuanwu-gateway/tests/test_bootstrap.py
git commit -m "feat: implement gateway sensor ingest adapters"
```

## Task 6: Implement industrial baseline adapters

**Files:**
- Create: `main/xuanwu-gateway/core/adapters/modbus_tcp_adapter.py`
- Create: `main/xuanwu-gateway/core/adapters/opc_ua_adapter.py`
- Create: `main/xuanwu-gateway/core/adapters/bacnet_ip_adapter.py`
- Create: `main/xuanwu-gateway/core/adapters/can_gateway_adapter.py`
- Modify: `main/xuanwu-gateway/core/registry/adapter_registry.py`
- Test: `main/xuanwu-gateway/tests/test_industrial_adapters.py`

- [ ] **Step 1: Write the failing tests**

Add tests with valid protocol-shaped payloads for:
- Modbus TCP read/write registers/coils
- OPC UA node read/write
- BACnet/IP object-property reads
- CAN gateway frame command/state requests

Assert:
- route validation
- request normalization
- result normalization
- protocol-level error normalization

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest main/xuanwu-gateway/tests/test_industrial_adapters.py -q`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement adapters using:
- deterministic pluggable transports in tests
- protocol-shaped command builders in production code
- optional runtime library bindings where present

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest main/xuanwu-gateway/tests/test_industrial_adapters.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-gateway/core/adapters/modbus_tcp_adapter.py main/xuanwu-gateway/core/adapters/opc_ua_adapter.py main/xuanwu-gateway/core/adapters/bacnet_ip_adapter.py main/xuanwu-gateway/core/adapters/can_gateway_adapter.py main/xuanwu-gateway/core/registry/adapter_registry.py main/xuanwu-gateway/tests/test_industrial_adapters.py
git commit -m "feat: implement gateway industrial adapters"
```

## Task 7: Implement wireless gateway baseline adapters

**Files:**
- Create: `main/xuanwu-gateway/core/adapters/bluetooth_adapter.py`
- Create: `main/xuanwu-gateway/core/adapters/nearlink_adapter.py`
- Modify: `main/xuanwu-gateway/core/registry/adapter_registry.py`
- Test: `main/xuanwu-gateway/tests/test_wireless_adapters.py`

- [ ] **Step 1: Write the failing tests**

Add tests with valid wireless protocol-shaped payloads for:
- Bluetooth characteristic read/write
- Bluetooth notification-backed state ingestion normalization
- NearLink command dispatch payload mapping
- NearLink state query normalization

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest main/xuanwu-gateway/tests/test_wireless_adapters.py -q`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Implement adapters with:
- deterministic fake transports in tests
- route validation for address, service/characteristic, and transport metadata
- normalized command results and state payloads

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest main/xuanwu-gateway/tests/test_wireless_adapters.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-gateway/core/adapters/bluetooth_adapter.py main/xuanwu-gateway/core/adapters/nearlink_adapter.py main/xuanwu-gateway/core/registry/adapter_registry.py main/xuanwu-gateway/tests/test_wireless_adapters.py
git commit -m "feat: implement gateway wireless adapters"
```

## Task 8: End-to-end verification and docs alignment

**Files:**
- Modify: `main/xuanwu-gateway/README.md`
- Modify: `docs/project/state/current.md`
- Modify: `docs/project/tasks/2026-03-30-platform-implementation-roadmap.md`
- Test: `main/xuanwu-gateway/tests/test_bootstrap.py`
- Test: `main/xuanwu-gateway/tests/test_dispatch.py`
- Test: `main/xuanwu-gateway/tests/test_registry.py`
- Test: `main/xuanwu-gateway/tests/test_http_adapter.py`
- Test: `main/xuanwu-gateway/tests/test_home_assistant_adapter.py`
- Test: `main/xuanwu-gateway/tests/test_mqtt_adapter.py`
- Test: `main/xuanwu-gateway/tests/test_sensor_ingest.py`
- Test: `main/xuanwu-gateway/tests/test_industrial_adapters.py`

- [ ] **Step 1: Write or update any missing failing verification tests**

Add regression assertions only if a verified gap remains after Tasks 1-6.

- [ ] **Step 2: Run the full gateway test suite**

Run: `python -m pytest main/xuanwu-gateway/tests -q`
Expected: PASS

- [ ] **Step 3: Run broader regression and syntax checks**

Run:

```bash
python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-gateway/tests -q
python -m py_compile main/xuanwu-gateway/app.py main/xuanwu-gateway/core/http_server.py main/xuanwu-gateway/core/api/gateway_handler.py main/xuanwu-gateway/core/registry/adapter_registry.py
```

Expected: PASS

- [ ] **Step 4: Update docs to match implementation**

Mark gateway adapters as implemented up to the actual completed set, and remove skeleton wording if no longer accurate.

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-gateway/README.md docs/project/state/current.md docs/project/tasks/2026-03-30-platform-implementation-roadmap.md main/xuanwu-gateway/tests
git commit -m "docs: finalize gateway adapter implementation status"
```
