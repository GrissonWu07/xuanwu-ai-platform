# Platform Implementation Roadmap

## Goal

Translate the active platform specs into working repository-local code and stop only at the point where upstream `XuanWu` integration becomes the remaining blocker.

## Phase Status

1. [x] `xuanwu-management-server` foundation
2. [x] `xuanwu-management-server` governance and read models
3. [x] `xuanwu-iot-gateway` foundation and adapter implementation
4. [x] `xuanwu-device-gateway` boundary cleanup
5. [x] `xuanwu-jobs` scheduler-dispatcher
6. [x] `xuanwu-portal` unified frontend
7. [x] device ingress convergence and discovered-device workflow
8. [x] wireless bridge services
9. [ ] upstream `XuanWu` contract integration

## Completed Local Phases

### 1. Management foundation

Completed:

- users
- channels
- devices
- runtime resolve
- baseline `XuanWu` proxy surfaces

### 2. Management governance and portal read models

Completed:

- auth login and logout and `auth/me`
- device lifecycle
- device import
- mappings
- capabilities and routes
- gateways
- OTA firmware and campaigns
- events, telemetry, alarms
- jobs schedules and runs
- dashboard, alerts, jobs, and gateway overview read models
- discovered-device APIs
- device detail aggregation

### 3. IoT gateway implementation

Completed:

- adapter registry
- commands and dispatch
- health and config endpoints
- ingest endpoints
- device-state endpoint
- protocol implementations for HTTP, MQTT, Home Assistant, Modbus TCP, OPC UA, BACnet/IP, CAN, Bluetooth, NearLink, and sensor ingress

### 4. Device gateway cleanup

Completed:

- conversational runtime boundary cleanup
- local runtime naming aligned to `XuanWu`
- control-plane hosting removed from the runtime service
- runtime job execution endpoint
- runtime-side device discovery and heartbeat callback

### 5. Jobs implementation

Completed:

- lightweight scheduler-dispatcher service
- due schedule polling
- claim and retry semantics
- cron progression
- dispatchable queued runs
- direct dispatch to management, IoT gateway, and device gateway execution APIs

### 6. Portal implementation

Completed:

- Vue 3 unified frontend
- top-tab primary navigation
- profile-menu workspaces
- live detail panels
- action flows for jobs, devices, channels, gateways, alerts, and discovered devices
- Docker and Nginx delivery path

### 7. Device ingress convergence

Completed:

- discovered-device model
- gateway-first discovery
- device-gateway first-contact discovery
- promote and ignore workflow
- unified device recency and heartbeat updates
- portal discovery review flow

### 8. Wireless bridge services

Completed:

- `xuanwu-bluetooth-bridge`
- `xuanwu-nearlink-bridge`
- Linux RPM packaging assets
- Windows Service packaging assets

## Remaining Phase

### 9. Upstream `XuanWu` integration

Still required from upstream:

- stable management APIs by contract
- stable worker and execution APIs by contract
- validated `XuanWu -> xuanwu-iot-gateway` device-action flow

Repository-local follow-up after upstream is ready:

- remove remaining local compatibility paths from `xuanwu-device-gateway`
- switch final device-action execution fully onto `XuanWu -> xuanwu-iot-gateway`
- validate end-to-end scheduled and interactive agent-driven invocation

## Practical Status

All repository-local roadmap work for the active spec set is complete.

The current roadmap blocker is upstream integration, not missing local platform implementation.
