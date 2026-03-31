# Spec Completion Status

## Purpose

This document summarizes which spec-defined areas are complete in this repository, which areas are only partially complete, and which areas are blocked on upstream `XuanWu`.

It is the implementation-oriented completion ledger for the current platform blueprint.

## Summary

### Completed locally

- `xuanwu-management-server` foundation and governance surfaces
- `xuanwu-device-server` local boundary cleanup
- `xuanwu-gateway` foundation plus protocol adapter implementation
- `xuanwu-jobs` lightweight scheduler-dispatcher
- `xuanwu-portal` unified frontend shell and current workspaces
- Docker-first local delivery path

### Partially complete locally

- `xuanwu-portal` deeper operational CRUD across every workspace
- `xuanwu-jobs` richer scheduling semantics
- `xuanwu-gateway` deeper platform depth beyond the adapter baseline:
  - broker-backed MQTT runtime operations
  - richer Home Assistant sync beyond state reads
  - deeper industrial browse/subscribe coverage

### Not locally completable without upstream

- Stable `XuanWu` management API integration
- Stable `XuanWu -> xuanwu-gateway` device command contract validation
- Final removal of residual local IoT/Home Assistant compatibility paths in `xuanwu-device-server`

## Completion Matrix

| Area | Spec status | Repository status | Notes |
| --- | --- | --- | --- |
| Platform blueprint | Defined | Complete | Active blueprint and index are in place |
| Management data model | Defined | Complete | User/device/channel/mapping/runtime model is live |
| Management governance APIs | Defined | Complete | Events, telemetry, alarms, OTA, mappings, schedules are live |
| Gateway contract | Defined | Complete | Contract is implemented through unified gateway surfaces |
| Gateway module blueprint | Defined | Complete | Registry, dispatch, ingest, and adapter families are implemented |
| Device-server boundary | Defined | Complete | Runtime service no longer hosts management paths |
| Jobs foundation | Defined | Complete | Local lightweight scheduler-dispatcher is live |
| Jobs advanced semantics | Defined implicitly | Partial | Pause/resume/trigger exist, but richer semantics are still pending |
| Portal design and frontend shell | Defined | Complete | Unified Vue 3 portal is live |
| Portal operational depth | Defined | Partial | Core pages exist, but not every workspace is fully actionable |
| Upstream `XuanWu` integration | Defined | Blocked upstream | Depends on upstream contract delivery |

## Completed Areas

### `xuanwu-management-server`

Completed:

- auth login/logout and `auth/me`
- users, roles, channels, devices
- device lifecycle actions
- batch device import
- mappings
- capabilities and routes
- gateways
- OTA firmware and campaigns
- events, telemetry, alarms
- gateway ingress
- jobs schedules and runs
- runtime resolve and binding views
- portal read models

### `xuanwu-device-server`

Completed:

- management-hosting removal
- local Python management path as default
- runtime naming aligned to `XuanWu`
- runtime job execution entrypoint
- local verification baseline updated

### `xuanwu-jobs`

Completed:

- standalone lightweight service
- due schedule polling
- claim against management server
- direct dispatch to local execution APIs
- Docker service delivery path

### `xuanwu-gateway`

Completed:

- HTTP actuator adapter
- MQTT actuator adapter
- Home Assistant service-call adapter
- sensor HTTP push ingest adapter
- sensor MQTT ingest adapter
- industrial adapters for:
  - Modbus TCP
  - OPC UA
  - BACnet/IP
  - CAN gateway
- wireless adapters for:
  - Bluetooth
  - NearLink
- gateway ingress surfaces for telemetry and event normalization

### `xuanwu-portal`

Completed:

- Vue 3 unified frontend
- `Overview / Devices / Agents / Jobs / Alerts`
- profile menu destinations
- Telemetry & Alarms workspace
- Docker + Nginx delivery path
- detail-backed drilldowns
- URL-backed workspace selection

## Partial Areas

### `xuanwu-portal` operational depth

Still incomplete:

- full CRUD parity across every profile-menu destination
- richer bulk actions on device, gateway, and alert surfaces
- broader operational actions on AI proxy pages beyond current upstream proxy reads

### `xuanwu-jobs` richer semantics

Still incomplete:

- richer schedule expressions beyond the current local interval baseline
- clearer retry / failure policy controls at the schedule definition level
- deeper run-history and operator controls in the portal

## Upstream-Blocked Areas

The following remain blocked on `XuanWu`:

- stable upstream agent/provider/model APIs
- stable upstream worker execution APIs
- final northbound device invocation contract from `XuanWu` into `xuanwu-gateway`
- integrated validation of agent-driven device actions

## Local Follow-up After Upstream Is Ready

- remove the remaining local IoT/Home Assistant compatibility paths from `xuanwu-device-server`
- switch final device action execution fully onto `XuanWu -> xuanwu-gateway`
- validate end-to-end agent-driven scheduled execution

## Current Priority

The highest-priority local unfinished spec area is:

1. `xuanwu-portal` deeper operational actions
2. `xuanwu-jobs` richer scheduling semantics
3. upstream `XuanWu` contract integration
