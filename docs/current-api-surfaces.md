# Current API Surfaces

## Purpose

This document summarizes the API surfaces that are already available and in active local use.

## Persistence Backing

These API surfaces now sit on PostgreSQL-backed persistence by default:

- management control-plane truth -> `xw_mgmt`
- IoT gateway device shadow/state -> `xw_iot`
- root deployment database files -> `deploy/postgres`

## `xuanwu-management-server`

Base area:

- `/control-plane/v1/*`

Current major surfaces:

- auth
  - `/auth/login`
  - `/auth/logout`
  - `/auth/me`
- users and roles
  - `/users`
  - `/users/{user_id}`
  - `/roles`
- channels and devices
  - `/channels`
  - `/channels/{channel_id}`
  - `/devices`
  - `/devices/{device_id}`
  - `/devices:batch-import`
  - `/devices/{device_id}:claim`
  - `/devices/{device_id}:bind`
  - `/devices/{device_id}:suspend`
  - `/devices/{device_id}:retire`
- discovered devices
  - `/discovered-devices`
  - `/discovered-devices/{discovery_id}`
  - `/discovered-devices/{discovery_id}:promote`
  - `/discovered-devices/{discovery_id}:ignore`
- mappings
  - `/mappings/user-devices`
  - `/mappings/user-channels`
  - `/mappings/channel-devices`
  - `/mappings/device-agents`
  - `/mappings/agent-model-providers`
  - `/mappings/agent-model-configs`
  - `/mappings/agent-knowledge`
  - `/mappings/agent-workflows`
- platform governance
  - `/events`
  - `/telemetry`
  - `/alarms`
  - `/alarms/{alarm_id}`
  - `/alarms/{alarm_id}:ack`
  - `/gateways`
  - `/gateways/{gateway_id}`
  - `/capabilities`
  - `/capability-routes`
  - `/ota/firmwares`
  - `/ota/campaigns`
- jobs
  - `/jobs/schedules`
  - `/jobs/schedules/{schedule_id}`
  - `/jobs/schedules/{schedule_id}:pause`
  - `/jobs/schedules/{schedule_id}:resume`
  - `/jobs/schedules/{schedule_id}:trigger`
  - `/jobs/runs`
  - `/jobs/runs/{job_run_id}`
  - `/jobs/runs/{job_run_id}:retry`
  - internal job execution and claim endpoints
- portal read models
  - `/dashboard/overview`
  - `/alerts/overview`
  - `/jobs/overview`
  - `/gateway/overview`
  - `/portal/config`
  - `/devices/{device_id}/detail`
- runtime and gateway ingress
  - runtime resolve and binding views
  - event, telemetry, command-result, discovery, and heartbeat ingress
- `XuanWu` proxy
  - `/xuanwu/agents`
  - `/xuanwu/model-providers`
  - `/xuanwu/models`

## `xuanwu-iot-gateway`

Base area:

- `/gateway/v1/*`

Current major surfaces:

- `/adapters`
- `/health`
- `/config`
- `/commands`
- `/commands:dispatch`
- `/jobs:execute`
- `/devices/{device_id}/state`
- `/ingest/http-push`
- `/ingest/mqtt`
- `/ingest/home-assistant`

## `xuanwu-device-gateway`

Base areas:

- `/xuanwu/ota/*`
- `/runtime/v1/*`

Current major surfaces:

- OTA and runtime connection entrypoints
- `/runtime/v1/jobs:execute`
- runtime session lookup and runtime-side execution endpoints

## `xuanwu-jobs`

Base area:

- `/jobs/v1/*`

Current major surfaces:

- `/health`
- `/config`

Operationally, `xuanwu-jobs` mainly interacts with management APIs instead of exposing a wide user-facing API surface.

## Which APIs Are Portal-Critical

The current portal depends primarily on:

- management auth and overview APIs
- devices, discovered devices, alarms, jobs, users, roles, channels, gateways, and settings read models
- job operator actions
- alarm acknowledge
- device and discovered-device actions

## Which APIs Are Internal Callback Surfaces

These are primarily service-to-service:

- discovery ingress
- heartbeat ingress
- telemetry ingress
- event ingress
- command-result ingress
- internal jobs claim and completion flows
