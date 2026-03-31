# xuanwu-jobs Foundation Design

## Goal

Add a fifth local service, `xuanwu-jobs`, that provides the minimum viable job scheduling and dispatch layer for this platform.

This phase is intentionally small:

- Docker-first, no Kubernetes work yet
- single lightweight jobs service
- direct API dispatch into local services
- no separate `xuanwu-jobs-worker` deployment surface
- no fake `XuanWu` execution logic inside this repository

## Why A Dedicated Jobs Service

`xuanwu-management-server` owns business truth:

- users
- devices
- channels
- mappings
- telemetry
- events
- alarms
- OTA metadata
- schedule definitions

`xuanwu-jobs` should not become another source of truth. It exists to:

- scan due schedules
- claim due schedules
- dispatch claimed jobs to the correct local service API
- leave Agent-domain execution to `XuanWu`
- leave device southbound execution to `xuanwu-gateway`

This keeps the boundary clean:

- `xuanwu-management-server`: what, who, state
- `xuanwu-jobs`: when and where
- `XuanWu` / `xuanwu-gateway` / `xuanwu-device-server`: how

## Scope

### In Scope

- create `main/xuanwu-jobs`
- add one scheduler-dispatcher entrypoint
- add dispatch adapters for:
  - `platform`
  - `gateway`
  - `device`
- add minimal schedule polling against `xuanwu-management-server`
- add direct execution endpoints in local services
- add one Docker Compose service:
  - `xuanwu-jobs`

### Out of Scope

- Kubernetes manifests
- upstream `XuanWu` agent execution implementation
- durable retry orchestration
- dead-letter UI
- autoscaling

## Architecture

### Service Topology

- `xuanwu-management-server`
  - stores schedules and exposes schedule APIs
  - executes local platform jobs through its own execution API
- `xuanwu-jobs`
  - scheduler process
  - direct dispatcher process
- `xuanwu-gateway`
  - executes gateway jobs through its own execution API
- `xuanwu-device-server`
  - executes runtime maintenance jobs through its own execution API
- future:
  - upstream `XuanWu` execution API for agent jobs

### Job Flow

1. A schedule exists in `xuanwu-management-server`
2. `xuanwu-jobs` polls for due schedules
3. `xuanwu-jobs` claims a due schedule
4. `xuanwu-jobs` dispatches the claimed job to the target service API
5. The target service executes the job in its own domain
6. `xuanwu-jobs` reports execution result back to `xuanwu-management-server`

## Job Types

This phase executes these local classes:

- `platform`
  - `telemetry_rollup`
  - `alarm_escalation`
  - `ota_campaign_tick`
- `gateway`
  - `device_command`
- `device`
  - `runtime_config_refresh`
  - `runtime_session_unregister`

Reserved but not executed locally in this phase:

- `agent`
  - `agent_run`
  - `workflow_run`

## Contracts

### Schedule Record

Minimum schedule shape returned by management:

```json
{
  "schedule_id": "sched-telemetry-001",
  "enabled": true,
  "job_type": "telemetry_rollup",
  "executor_type": "platform",
  "cron_expr": "*/5 * * * *",
  "timezone": "Asia/Shanghai",
  "next_run_at": "2026-03-31T10:00:00Z",
  "payload": {
    "site_id": "site-a"
  }
}
```

### Claimed Job Payload

Minimum claimed job payload:

```json
{
  "job_run_id": "run-sched-telemetry-001-20260331T100000Z",
  "schedule_id": "sched-telemetry-001",
  "job_type": "telemetry_rollup",
  "executor_type": "platform",
  "scheduled_for": "2026-03-31T10:00:00Z",
  "payload": {
    "site_id": "site-a"
  }
}
```

### APIs Needed

`xuanwu-jobs` depends on these control-plane APIs:

- `GET /control-plane/v1/jobs/schedules:due`
- `POST /control-plane/v1/jobs/schedules/{schedule_id}:claim`
- `POST /control-plane/v1/jobs/runs/{job_run_id}:complete`
- `POST /control-plane/v1/jobs/runs/{job_run_id}:fail`

This phase also adds direct execution endpoints for local dispatch:

- `POST /control-plane/v1/jobs:execute`
- `POST /gateway/v1/jobs:execute`
- `POST /runtime/v1/jobs:execute`

Future upstream contract:

- `POST /xuanwu/v1/jobs:execute`

## Implementation Notes

- keep code layout parallel to the other Python services
- do not embed schedule truth into `xuanwu-jobs`
- do not add fake local `XuanWu` execution
- keep `xuanwu-jobs` lightweight and non-authoritative
- do not design `xuanwu-jobs` as the main horizontal scaling surface

## Verification Target

The completion bar for this phase is:

- `xuanwu-jobs` starts locally
- scheduler can claim and dispatch a due platform job
- local services expose execution endpoints for `platform`, `gateway`, and `device`
- Docker Compose includes a single `xuanwu-jobs` service
- no Redis or `xuanwu-jobs-worker` dependency remains in the local path
