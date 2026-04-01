# Current Platform Capabilities

## Purpose

This document describes what the repository can do today without depending on unfinished upstream `XuanWu` work.

## Core Services

The current local platform consists of:

- `xuanwu-management-server`
- `xuanwu-device-gateway`
- `xuanwu-iot-gateway`
- `xuanwu-jobs`
- `xuanwu-portal`
- `xuanwu-bluetooth-bridge`
- `xuanwu-nearlink-bridge`

## Default Persistence

The platform now defaults to PostgreSQL-backed persistence:

- `xuanwu-management-server` uses schema `xw_mgmt`
- `xuanwu-iot-gateway` uses schema `xw_iot`
- root Docker deployment stores PostgreSQL data under `deploy/data/pg`

## Management Capabilities

`xuanwu-management-server` currently supports:

- users
- roles
- channels
- managed devices
- discovered devices
- device lifecycle actions
- user, channel, and agent mappings
- capabilities and capability routes
- gateways
- OTA firmware and OTA campaigns
- events
- telemetry
- alarms
- jobs schedules and runs
- portal-facing overview and detail read models

## Conversational Device Capabilities

`xuanwu-device-gateway` currently supports:

- conversational device ingress
- runtime session handling
- OTA entrypoints
- runtime config resolution from management
- first-contact discovery callback into management
- runtime heartbeat callback into management
- local runtime job execution

## IoT and Industrial Capabilities

`xuanwu-iot-gateway` currently supports:

- command dispatch
- protocol adapter registry
- telemetry and event ingest
- device state lookup
- management callbacks for discovery, heartbeat, and command results

Current implemented protocol families:

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

## Scheduling Capabilities

`xuanwu-jobs` currently supports:

- due-schedule polling
- claim against management
- direct dispatch to local execution APIs
- cron progression
- queued dispatchable runs
- retry scheduling metadata
- operator-triggered retry flow

## Portal Capabilities

`xuanwu-portal` currently supports:

- unified shell with no left navigation
- top-tab navigation
- overview dashboard
- devices workspace
- agents workspace
- jobs workspace
- alerts workspace
- profile-menu workspaces for users, channels, gateways, AI config proxy, telemetry, settings, and sign out
- drilldown panels
- query-backed selected-object context
- device discovery review and promotion

## Wireless Bridge Capabilities

The repository also contains local standalone services for:

- Bluetooth bridge
- NearLink bridge

Each includes:

- HTTP service scaffolding
- callback integration path
- Linux RPM packaging assets
- Windows Service packaging assets

## What Is Still Upstream-Dependent

The following are not complete locally because they depend on `XuanWu`:

- stable upstream management APIs
- stable upstream execution APIs
- final agent-driven device invocation through `xuanwu-iot-gateway`
- final cleanup of residual local compatibility paths after upstream validation
