# Spec Completion Status

## Purpose

This document summarizes which spec-defined areas are complete in this repository, which areas remain optional local enhancements, and which areas are blocked on upstream `XuanWu`.

It is the implementation-oriented completion ledger for the current platform blueprint.

## Summary

### Completed locally

- `xuanwu-management-server` foundation and governance surfaces
- `xuanwu-device-gateway` local boundary cleanup
- `xuanwu-iot-gateway` foundation plus protocol adapter implementation
- `xuanwu-jobs` lightweight scheduler-dispatcher
- `xuanwu-jobs` richer schedule semantics for cron, retry, queued dispatch, and operator actions
- `xuanwu-portal` unified frontend shell and current workspaces
- device ingress integration across `xuanwu-management-server`, `xuanwu-iot-gateway`, and `xuanwu-device-gateway`
- standalone wireless bridge services:
  - `xuanwu-bluetooth-bridge`
  - `xuanwu-nearlink-bridge`
- Docker-first local delivery path

### Not locally completable without upstream

- Stable `XuanWu` management API integration
- Stable `XuanWu -> xuanwu-iot-gateway` device command contract validation
- Final removal of residual local IoT/Home Assistant compatibility paths in `xuanwu-device-gateway`

## Completion Matrix

| Area | Spec status | Repository status | Notes |
| --- | --- | --- | --- |
| Platform blueprint | Defined | Complete | Active blueprint and index are in place |
| Management data model | Defined | Complete | User/device/channel/mapping/runtime model is live |
| Management governance APIs | Defined | Complete | Events, telemetry, alarms, OTA, mappings, schedules are live |
| Gateway contract | Defined | Complete | Contract is implemented through unified gateway surfaces |
| Gateway module blueprint | Defined | Complete | Registry, dispatch, ingest, and adapter families are implemented |
| Gateway adapter completion | Defined | Complete locally | MQTT, Home Assistant, Modbus, OPC UA, BACnet/IP, CAN, Bluetooth, and NearLink baseline depth are implemented |
| Device-server boundary | Defined | Complete | Runtime service no longer hosts management paths |
| Jobs foundation | Defined | Complete | Local lightweight scheduler-dispatcher is live |
| Jobs advanced semantics | Defined implicitly | Complete locally | Cron progression, retry, dispatchable runs, and portal operator actions are live |
| Portal design and frontend shell | Defined | Complete | Unified Vue 3 portal is live |
| Portal operational depth | Defined | Complete for current spec set | Devices, Jobs, Alerts, Users/Roles, Channels/Gateways, AI proxy, Settings, and Telemetry/Alarms all have live workspace surfaces |
| Wireless bridge services | Defined | Complete locally | Bluetooth and NearLink bridge services, packaging assets, and gateway callback contracts are implemented |
| Device ingress integration | Defined | Complete locally | Discovered-device layer, promotion flow, gateway/runtime callbacks, and portal discovery workflows are live |
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
- discovered-device store and APIs
- discovered-device promotion and ignore workflow
- device heartbeat and recency updates
- richer device-detail aggregation with discovery provenance and latest command result

### `xuanwu-device-gateway`

Completed:

- management-hosting removal
- local Python management path as default
- runtime naming aligned to `XuanWu`
- runtime job execution entrypoint
- runtime discovery callback into management
- runtime heartbeat callback into management
- local verification baseline updated

### `xuanwu-jobs`

Completed:

- standalone lightweight service
- due schedule polling
- claim against management server
- direct dispatch to local execution APIs
- cron schedule progression
- dispatchable run polling
- manual retry enqueue and claim flow
- Docker service delivery path

### `xuanwu-iot-gateway`

Completed:

- HTTP actuator adapter
- MQTT actuator adapter
- MQTT broker-message ingest normalization
- Home Assistant service-call adapter
- Home Assistant state read and state-change ingest
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
- gateway device-discovery callback into management
- gateway heartbeat and recency callback into management
- bridge callback validation against Bluetooth and NearLink bridge services

### `xuanwu-portal`

Completed:

- Vue 3 unified frontend
- `Overview / Devices / Agents / Jobs / Alerts`
- profile menu destinations
- Telemetry & Alarms workspace
- Docker + Nginx delivery path
- detail-backed drilldowns
- URL-backed workspace selection
- discovered-device review, promote, and ignore workflows
- channel and gateway operational actions
- job pause, resume, trigger, and retry actions
- policy display for misfire and retry semantics

### Wireless bridge services

Completed:

- standalone `xuanwu-bluetooth-bridge`
- standalone `xuanwu-nearlink-bridge`
- Linux RPM service packaging assets
- Windows Service packaging assets
- HTTP APIs, runtime scaffolds, callback clients, and packaging docs

## Optional Future Enhancements

These are not current spec blockers:

- fuller RBAC editing UX
- richer AI proxy editing once upstream `XuanWu` forms are available
- deeper run-history analytics in the portal
- real-environment validation against physical brokers, industrial networks, and bridge hardware

## Upstream-Blocked Areas

The following remain blocked on `XuanWu`:

- stable upstream agent/provider/model APIs
- stable upstream worker execution APIs
- final northbound device invocation contract from `XuanWu` into `xuanwu-iot-gateway`
- integrated validation of agent-driven device actions

## Local Follow-up After Upstream Is Ready

- remove the remaining local IoT/Home Assistant compatibility paths from `xuanwu-device-gateway`
- switch final device action execution fully onto `XuanWu -> xuanwu-iot-gateway`
- validate end-to-end agent-driven scheduled execution

## Current Priority

The remaining highest-priority implementation area is upstream:

1. `XuanWu` management and execution contract integration
2. end-to-end `XuanWu -> xuanwu-iot-gateway` validation
3. retirement of final local compatibility paths after upstream validation
