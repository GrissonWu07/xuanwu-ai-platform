# Platform Implementation Roadmap

## Scope
- Turn the active platform specs into repository-local implementation work.
- Finish all local management, gateway, runtime-boundary, bridge, jobs, and portal work in this repository.
- Leave Agent-domain source-of-truth work to `XuanWu`.

## Status
1. [x] Phase 1: `xuanwu-management-server` foundation
2. [x] Phase 2: `xuanwu-management-server` governance surfaces
3. [x] Phase 3: `xuanwu-iot-gateway` foundation and adapter skeletons
4. [x] Phase 4: `xuanwu-device-gateway` boundary cleanup
5. [x] Phase 5: `xuanwu-jobs` foundation and direct local dispatch
6. [x] Phase 6: `xuanwu-portal` Phase 1 and Phase 2 shell delivery
7. [ ] Phase 7: upstream `XuanWu` integration and contract validation

## Completed Locally

### Phase 1: `xuanwu-management-server` foundation
- Implemented:
  - users
  - channels
  - devices
  - runtime resolve
  - base `XuanWu` proxy surfaces
- Verified with local management server tests.

### Phase 2: `xuanwu-management-server` governance surfaces
- Implemented:
  - auth login/logout
  - device lifecycle
  - batch device import
  - all local mapping surfaces
  - capabilities, routes, gateways
  - OTA firmware and campaigns
  - unified events, telemetry, alarms
  - gateway ingress APIs
  - event/telemetry filtering
  - mirrored `command.result` event creation
- Verified with store, handler, and HTTP route tests.

### Phase 3: `xuanwu-iot-gateway` foundation
- Implemented:
  - standalone app bootstrap
  - adapter registry
  - command dispatch
  - adapter inventory endpoint
  - health/config/device-state endpoints
  - ingest endpoints for HTTP push and MQTT telemetry
  - adapter directory layout for conversation, actuator, sensor, industrial, and wireless classes
  - implemented adapter families:
    - `http`
    - `mqtt`
    - `home_assistant`
    - `sensor_http_push`
    - `sensor_mqtt`
    - `modbus_tcp`
    - `opc_ua`
    - `bacnet_ip`
    - `can_gateway`
    - `bluetooth`
    - `nearlink`
- Verified with bootstrap, registry, and dispatch tests.

### Phase 3a: `xuanwu-iot-gateway` protocol depth and wireless bridges
- Implemented:
  - MQTT broker-message normalization
  - Home Assistant state ingest
  - Modbus TCP baseline reads and writes
  - OPC UA browse/read/write
  - BACnet/IP multi-property reads
  - CAN bridge query routing
  - standalone `xuanwu-bluetooth-bridge`
  - standalone `xuanwu-nearlink-bridge`
  - Linux RPM packaging assets for both bridge services
  - Windows Service packaging assets for both bridge services
- Verified with gateway, bridge, and bridge-callback test suites.

### Phase 4: `xuanwu-device-gateway` boundary cleanup
- Implemented:
  - runtime naming cleanup to `XuanWu`
  - `xuanwu_session_key`
  - management hosting removed from runtime service
  - runtime tests aligned to new management server path
- Verified with device-server regression tests.

### Phase 4a: device ingress convergence
- Implemented:
  - discovered-device layer in management
  - gateway device-discovery callback
  - device-server first-contact discovery callback
  - unified device heartbeat and recency updates
  - device detail provenance aggregation
  - portal discovered-device review and promotion flow
- Verified with management, gateway, device-server, and portal test coverage.

### Phase 5: `xuanwu-jobs` foundation
- Implemented:
  - `main/xuanwu-jobs`
  - local due-schedule and job-run APIs in `xuanwu-management-server`
  - lightweight scheduler-dispatcher in `xuanwu-jobs`
  - direct execution APIs in:
    - `xuanwu-management-server`
    - `xuanwu-iot-gateway`
    - `xuanwu-device-gateway`
  - Docker Compose service for `xuanwu-jobs`
  - cron progression
  - dispatchable queued run polling
  - retry enqueue and claim semantics

### Phase 6: `xuanwu-portal` shell delivery
- Implemented:
  - new Vue 3 portal in `main/xuanwu-portal`
  - dedicated Docker image and compose service for `xuanwu-portal`
  - Nginx reverse-proxy entrypoint for management, gateway, runtime, and jobs APIs
  - unified shell with `Overview / Devices / Agents / Jobs / Alerts`
  - Phase 1 primary work pages
  - Phase 2 profile-menu destinations:
    - `Users & Roles`
    - `Channels & Gateways`
    - `AI Config Proxy`
    - `Settings`
    - `Sign out`
    - `Telemetry & Alarms`
  - query-backed detail selection for:
    - `Users & Roles`
    - `Channels & Gateways`
    - `AI Config Proxy`
    - `Settings`
    - `Telemetry & Alarms`
  - portal-facing management read models
  - detail-backed drilldown on:
    - `Jobs` via schedule and run detail APIs
    - `Alerts` via alarm detail API
    - profile destinations via selected-object detail panels, including feature flags and service endpoints in `Settings`
  - actionable `Overview` quick cards that route into the corresponding primary workspaces
  - actionable `Overview` live activity items that route into deep-linked object workspaces
  - deep-linkable workspace selection on:
    - `Devices`
    - `Agents`
    - `Jobs`
    - `Alerts`
  - `Channels & Gateways` upgraded from raw lists to a live gateway overview view with protocol and site distribution
  - discovered-device review and promote/ignore actions in `Devices`
  - channel and gateway state actions in `Channels & Gateways`
  - job pause, resume, trigger, retry, and policy visibility in `Jobs`
- Verified with portal unit tests and `vite` production build.

## Remaining

### Phase 7: upstream `XuanWu` integration
- Required from upstream:
  - stable `XuanWu` management APIs by contract
  - stable northbound command contract from `XuanWu` to `xuanwu-iot-gateway`
  - integration validation for device capability invocation
- Repository-local follow-up after upstream is ready:
  - remove remaining local IoT/Home Assistant compatibility paths from `xuanwu-device-gateway`
  - switch final device-action execution fully onto `XuanWu -> xuanwu-iot-gateway`

## Local Completion Status

All repository-local phases for the current spec set are complete.

The only remaining roadmap item is upstream `XuanWu` integration and the final cleanup that depends on it.

## Verification
- command:
  - `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-iot-gateway/tests/test_dispatch.py main/xuanwu-iot-gateway/tests/test_sensor_ingest.py main/xuanwu-iot-gateway/tests/test_bridge_callbacks.py main/xuanwu-device-gateway/tests/test_local_control_plane.py main/xuanwu-jobs/tests/test_scheduler_contract.py main/xuanwu-bluetooth-bridge/tests main/xuanwu-nearlink-bridge/tests tests/test_wireless_bridge_layout.py -q`
- expected:
  - local platform work stays green
- actual:
  - `83 passed`

- command:
  - `npm test`
  - `npm run build`
  - cwd: `main/xuanwu-portal`
- expected:
  - portal shell and workspaces stay green
  - production bundle builds successfully
- actual:
  - portal unit tests green
  - `vite` production build green

- command:
  - `python -m py_compile main/xuanwu-management-server/app.py main/xuanwu-management-server/core/http_server.py main/xuanwu-management-server/core/api/control_plane_handler.py main/xuanwu-management-server/core/store/local_store.py main/xuanwu-iot-gateway/app.py main/xuanwu-iot-gateway/core/http_server.py main/xuanwu-iot-gateway/core/api/gateway_handler.py main/xuanwu-iot-gateway/core/clients/management_client.py main/xuanwu-iot-gateway/core/adapters/bluetooth_adapter.py main/xuanwu-iot-gateway/core/adapters/nearlink_adapter.py main/xuanwu-jobs/app.py main/xuanwu-jobs/core/scheduler.py main/xuanwu-jobs/core/clients/management_client.py main/xuanwu-device-gateway/app.py main/xuanwu-device-gateway/config/xuanwu_management_client.py main/xuanwu-bluetooth-bridge/app.py main/xuanwu-bluetooth-bridge/core/http_server.py main/xuanwu-bluetooth-bridge/core/api/bridge_handler.py main/xuanwu-nearlink-bridge/app.py main/xuanwu-nearlink-bridge/core/http_server.py main/xuanwu-nearlink-bridge/core/api/bridge_handler.py`
- expected:
  - syntax validation passes
- actual:
  - passed

## Handoff Notes
- Local implementation work is complete for the current spec set.
- The only remaining major implementation phase depends on upstream `XuanWu` contract delivery.
- Additional local work from here is optional enhancement unless it unblocks that upstream integration.
