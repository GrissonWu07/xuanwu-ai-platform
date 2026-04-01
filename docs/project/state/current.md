# Current State

## Objective

Finish every repository-local platform capability in this repository while keeping all Agent-domain truth in `XuanWu`.

The active local platform now consists of:

- `xuanwu-management-server`
- `xuanwu-device-gateway`
- `xuanwu-iot-gateway`
- `xuanwu-jobs`
- `xuanwu-portal`
- `xuanwu-bluetooth-bridge`
- `xuanwu-nearlink-bridge`

## What Is Complete Locally

### Unified platform structure

- `xuanwu-management-server` is the local source of truth for users, devices, channels, mappings, events, telemetry, alarms, OTA, schedules, and portal read models.
- `xuanwu-device-gateway` is the runtime ingress for conversational devices.
- `xuanwu-iot-gateway` is the ingress and execution layer for IoT, industrial, sensor, and wireless devices.
- `xuanwu-jobs` is the lightweight scheduler-dispatcher.
- `xuanwu-portal` is the single frontend entrypoint.

### Device management and ingress

- Managed-device records are live in `xuanwu-management-server`.
- Discovered-device records are live for first-contact devices from both ingress paths.
- `xuanwu-iot-gateway` reports discovery, telemetry, events, command results, and heartbeat into management.
- `xuanwu-device-gateway` reports first-contact discovery and runtime heartbeat into management.
- Portal now supports discovered-device review and promote or ignore actions.

### Gateway and protocol support

`xuanwu-iot-gateway` now implements the current local protocol surface for:

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

Wireless bridge services also exist locally:

- `xuanwu-bluetooth-bridge`
- `xuanwu-nearlink-bridge`

Both have Linux RPM packaging assets and Windows Service packaging assets.

### Jobs and scheduling

`xuanwu-jobs` now supports:

- due-schedule polling
- claim against management
- direct dispatch to platform, gateway, and device execution APIs
- cron progression
- queued dispatchable runs
- retry scheduling and operator-triggered retry

### Portal delivery

`xuanwu-portal` now provides these live workspaces:

- `Overview`
- `Devices`
- `Agents`
- `Jobs`
- `Alerts`
- `Users & Roles`
- `Channels & Gateways`
- `AI Config Proxy`
- `Telemetry & Alarms`
- `Settings`
- `Sign out`

Portal delivery is Docker-first and uses Nginx proxying for:

- `/control-plane`
- `/gateway`
- `/runtime`
- `/jobs`

## What Is Not Complete Locally

The remaining major work is upstream, not repository-local:

- stable `XuanWu` management APIs by contract
- stable `XuanWu -> xuanwu-iot-gateway` execution contract
- final end-to-end validation of agent-driven device invocation

## Current Boundary

- Local repository owns device management, ingress, gateway routing, scheduling, and portal delivery.
- `XuanWu` owns Agent truth, workflow truth, model truth, and final agent-driven execution decisions.

## Current Delivery Status

Repository-local implementation for the active spec set is complete.

Further local changes are optional enhancements unless they directly unblock upstream `XuanWu` integration.
