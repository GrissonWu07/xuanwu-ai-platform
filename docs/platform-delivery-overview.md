# Platform Delivery Overview

## Purpose

This document is the delivery-oriented overview for the current repository state.

Use it when you need a quick answer to:

- what services exist
- what each service is responsible for
- what is already complete locally
- what still depends on `XuanWu`
- where to start for deployment, integration, or operator handoff

## Active Local Services

### `xuanwu-management-server`

Role:

- platform control plane
- source of truth for users, devices, channels, mappings, telemetry, events, alarms, OTA, schedules, and portal read models

### `xuanwu-device-gateway`

Role:

- conversational device ingress
- runtime session handling
- OTA entrypoints
- runtime-side execution and heartbeat callback

### `xuanwu-iot-gateway`

Role:

- IoT and industrial protocol ingress
- protocol adaptation
- device command execution
- telemetry and event normalization

### `xuanwu-jobs`

Role:

- lightweight scheduler-dispatcher
- due schedule polling
- direct dispatch to platform, gateway, and device execution APIs

### `xuanwu-portal`

Role:

- single frontend entrypoint
- operator workflows
- unified portal for management, device, gateway, alerts, jobs, and overview

### `xuanwu-bluetooth-bridge`

Role:

- standalone Bluetooth bridge service

### `xuanwu-nearlink-bridge`

Role:

- standalone NearLink bridge service

## Current Device Model

The system now has two ingress paths that converge into the same management truth:

- `xuanwu-device-gateway` for conversational devices
- `xuanwu-iot-gateway` for IoT, industrial, sensor, and actuator devices

Both feed into:

- `discovered_device`
- then `managed_device`

Management remains the only durable truth.

## Current Closed Loops

### Device ingress loop

- gateway or device-gateway discovers a device
- management stores a discovered-device record
- portal shows the pending device
- operator promotes or ignores it
- management creates or updates the managed-device record

### Telemetry and event loop

- ingress services send telemetry, events, command results, and heartbeat
- management stores them
- portal reads them through management-owned read models

### Job loop

- management stores schedule truth
- `xuanwu-jobs` polls due schedules
- `xuanwu-jobs` dispatches to management, IoT gateway, or device gateway execution APIs
- results flow back into management

## Current Portal Scope

Primary workspaces:

- Overview
- Devices
- Agents
- Jobs
- Alerts

Profile-menu workspaces:

- Users & Roles
- Channels & Gateways
- AI Config Proxy
- Telemetry & Alarms
- Settings
- Sign out

## Current Protocol Coverage

`xuanwu-iot-gateway` currently includes local implementation for:

- HTTP
- MQTT
- Home Assistant
- sensor HTTP push
- sensor MQTT
- Modbus TCP
- OPC UA
- BACnet/IP
- CAN gateway
- Bluetooth
- NearLink

## Deployment Shape

Current local delivery is Docker-first.

Portal delivery uses Nginx to proxy:

- `/control-plane` -> `xuanwu-management-server`
- `/gateway` -> `xuanwu-iot-gateway`
- `/runtime` -> `xuanwu-device-gateway`
- `/jobs` -> `xuanwu-jobs`

## What Is Complete

The repository-local implementation for the active spec set is complete.

That includes:

- management
- device ingress
- IoT ingress
- scheduler-dispatcher
- portal
- wireless bridge services

## What Still Depends on `XuanWu`

The remaining major blocker is upstream integration:

- stable upstream management APIs
- stable upstream execution APIs
- validated `XuanWu -> xuanwu-iot-gateway` device action flow
- final retirement of residual local compatibility paths after upstream validation

## Recommended Reading

- [Quick Start](./quick-start.md)
- [Deployment Guide](./Deployment.md)
- [Current Platform Capabilities](./current-platform-capabilities.md)
- [Current API Surfaces](./current-api-surfaces.md)
- [Device Ingress and Management Guide](./device-ingress-and-management-guide.md)
- [Current State](./project/state/current.md)
- [Spec Completion Status](./superpowers/specs/2026-03-31-spec-completion-status.md)
