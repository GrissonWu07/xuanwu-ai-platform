# Platform API Completion Spec

Date: 2026-03-31

## Purpose

This spec defines the backend API work still required inside this repository to support `xuanwu-portal`.

It covers only local services:

- `xuanwu-management-server`
- `xuanwu-iot-gateway`
- `xuanwu-device-gateway`
- `xuanwu-jobs`

All `XuanWu` requirements are intentionally split into a dedicated upstream spec.

## Current Status

The repository already has enough APIs to start the first frontend implementation, but the API surface is not yet complete or ergonomic enough for a unified product frontend.

The strongest backend today is:

- `xuanwu-management-server`

The weakest frontend-facing areas today are:

- dashboard aggregation
- roles/profile APIs
- richer gateway read models
- richer jobs read models

## Service Ownership

### `xuanwu-management-server`

Owns:

- auth
- users
- channels
- devices
- mappings
- capabilities
- ota
- telemetry
- events
- alarms
- schedules
- job runs
- runtime resolve views
- `XuanWu` management proxy

### `xuanwu-iot-gateway`

Owns:

- adapter inventory
- gateway runtime health
- device command execution
- gateway-side device state lookup

### `xuanwu-device-gateway`

Owns:

- OTA serving
- runtime session APIs
- runtime speech / interrupt / tool execution
- device runtime job execution endpoint

### `xuanwu-jobs`

Owns:

- scheduler health
- scheduler config
- internal dispatch behavior

## API Gaps To Close

### 1. Dashboard Aggregation API

Problem:

`Overview` currently has to compose too many calls on the frontend.

Required new endpoint:

- `GET /control-plane/v1/dashboard/overview`

Recommended response sections:

- `summary`
- `activity`
- `device_summary`
- `jobs_summary`
- `alerts_summary`
- `gateway_summary`

Why:

- keeps `Overview` fast
- gives the portal one stable contract
- avoids stitching five to ten requests on first load

### 2. Profile and Session API

Problem:

The portal shell needs a clean top-right profile model, but only `login/logout` exist.

Required endpoints:

- `GET /control-plane/v1/auth/me`
- `GET /control-plane/v1/roles`

Recommended response for `/auth/me`:

- `user_id`
- `display_name`
- `avatar_url`
- `email`
- `role_ids`
- `permissions`

Recommended response for `/roles`:

- list of role definitions
- display label
- description
- effective permissions summary

### 3. Jobs Read Model API

Problem:

The current jobs APIs are useful for the scheduler but not ideal for a richer portal experience.

Required additions:

- `GET /control-plane/v1/jobs/schedules/{schedule_id}`
- `GET /control-plane/v1/jobs/runs/{job_run_id}`
- `GET /control-plane/v1/jobs/overview`

Recommended `jobs/overview` contents:

- scheduler health summary
- running count
- recent failures
- dispatch lag
- queue-free executor distribution summary

### 4. Alerts Read Model API

Problem:

Alert list and ack exist, but the portal will benefit from richer drilldown.

Required additions:

- `GET /control-plane/v1/alarms/{alarm_id}`
- `GET /control-plane/v1/alerts/overview`

Recommended `alerts/overview` contents:

- severity counts
- ack pending count
- escalated today
- top active sources

### 5. Devices Read Model API

Problem:

Device list and runtime views exist, but the Devices page needs a stronger detail shape.

Required additions:

- `GET /control-plane/v1/devices/{device_id}/detail`

Recommended contents:

- device
- owner summary
- channel memberships
- agent binding
- runtime binding view
- capability routing view
- recent events
- latest telemetry snapshot

### 6. Gateway Read Model API

Problem:

Gateway service currently exposes operational APIs, but the portal needs a management-facing read shape.

Preferred approach:

- expose a management-facing aggregation through `xuanwu-management-server`

Required endpoint:

- `GET /control-plane/v1/gateway/overview`

Optional direct gateway additions:

- `GET /gateway/v1/adapters/{adapter_id}`
- `GET /gateway/v1/adapters/{adapter_id}/health`

### 7. Portal Shell Configuration API

Problem:

The frontend needs one stable place for feature flags and runtime URLs.

Required endpoint:

- `GET /control-plane/v1/portal/config`

Recommended contents:

- feature flags
- visible modules
- upstream status indicators
- documentation links
- environment markers

## Existing APIs Good Enough For Phase 1

These can already support first delivery with only minor frontend adaptation:

- `GET/POST/PUT/DELETE /control-plane/v1/users`
- `GET/POST/PUT/DELETE /control-plane/v1/channels`
- `GET/POST/PUT /control-plane/v1/devices`
- `POST /control-plane/v1/devices:batch-import`
- lifecycle actions on devices
- `GET/POST /control-plane/v1/events`
- `GET/POST /control-plane/v1/telemetry`
- `GET /control-plane/v1/alarms`
- `POST /control-plane/v1/alarms/{alarm_id}:ack`
- `GET/POST /control-plane/v1/jobs/schedules`
- `GET /control-plane/v1/jobs/runs`

## Frontend Blocking Classification

### Not blocking Phase 1

- full role editor
- full settings editor
- deep OTA campaign editor
- rich gateway editing

### Soft blockers

These should be added before the frontend hardens:

- dashboard overview API
- `auth/me`
- roles list
- jobs overview
- alerts overview
- device detail
- portal config

## Delivery Order

Recommended backend completion order:

1. `GET /control-plane/v1/auth/me`
2. `GET /control-plane/v1/dashboard/overview`
3. `GET /control-plane/v1/portal/config`
4. `GET /control-plane/v1/jobs/overview`
5. `GET /control-plane/v1/alerts/overview`
6. `GET /control-plane/v1/devices/{device_id}/detail`
7. `GET /control-plane/v1/roles`
8. gateway overview aggregation

## Acceptance Criteria

This API completion work is complete when:

- `Overview` can render from a stable dashboard API
- the top-right profile menu can render from `auth/me`
- `Devices`, `Jobs`, and `Alerts` pages each have one detail or overview read model beyond raw collections
- gateway operational status can be shown without frontend guesswork
- the frontend no longer has to over-compose basic page data from too many low-level endpoints
