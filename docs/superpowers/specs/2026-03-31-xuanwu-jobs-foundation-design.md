# xuanwu-jobs Foundation Design

## Goal

Add a fifth local service, `xuanwu-jobs`, that provides the minimum viable distributed job triggering layer for this platform.

This first phase is intentionally small:

- Docker-first, no Kubernetes work yet
- Redis-backed queueing
- horizontally scalable workers by replica count
- local platform tasks only
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
- enqueue jobs
- run local platform jobs
- leave Agent-domain execution to `XuanWu`
- leave device southbound execution to `xuanwu-gateway`

This keeps the boundary clean:

- `xuanwu-management-server`: what, who, state
- `xuanwu-jobs`: when
- `XuanWu` / `xuanwu-gateway`: how

## Scope

### In Scope

- create `main/xuanwu-jobs`
- add Redis-backed job queue with ARQ
- add one scheduler entrypoint
- add one platform worker entrypoint
- define queue names for future worker classes:
  - `platform`
  - `agent`
  - `gateway`
- add minimal schedule polling against `xuanwu-management-server`
- add Docker Compose services for:
  - `redis`
  - `xuanwu-jobs-scheduler`
  - `xuanwu-jobs-platform-worker`
- make worker scale-out possible by increasing container replica count

### Out of Scope

- Kubernetes manifests
- `XuanWu` worker implementation
- `xuanwu-gateway` worker implementation
- full durable job database in this repo
- advanced retry orchestration
- dead-letter UI
- HPA or queue-depth autoscaling

## Architecture

### Service Topology

- `xuanwu-management-server`
  - stores schedules and exposes schedule APIs
- `xuanwu-jobs`
  - scheduler process
  - platform worker process
- `redis`
  - shared queue backend
- future:
  - `XuanWu` agent worker
  - `xuanwu-gateway` gateway worker

### Job Flow

1. A schedule exists in `xuanwu-management-server`
2. `xuanwu-jobs` scheduler polls for due schedules
3. Scheduler claims due schedules and calculates next execution time
4. Scheduler enqueues a job into Redis
5. A worker consumes the job
6. Worker executes the local platform task or forwards to another executor contract later
7. Worker reports execution result back to `xuanwu-management-server`

## Job Types

This phase only executes `platform` jobs locally. Supported examples:

- `telemetry_rollup`
- `alarm_escalation`
- `ota_campaign_tick`

Reserved but not executed locally in this phase:

- `agent_run`
- `workflow_run`
- `device_command`

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

### Queue Message

Minimum enqueued message:

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

### Management APIs Needed

This phase assumes these endpoints in `xuanwu-management-server`:

- `GET /control-plane/v1/jobs/schedules:due`
- `POST /control-plane/v1/jobs/schedules/{schedule_id}:claim`
- `POST /control-plane/v1/jobs/runs`
- `POST /control-plane/v1/jobs/runs/{job_run_id}:complete`
- `POST /control-plane/v1/jobs/runs/{job_run_id}:fail`

If they do not exist yet, this phase adds local placeholder implementations in `xuanwu-management-server`.

## Horizontal Scaling Model

### Scheduler

For this first phase, keep one active scheduler container by default in Docker Compose.

Reason:

- simplest safe rollout
- avoids duplicate schedule claims before we add stronger distributed claim verification

Later scaling can add multiple scheduler replicas once claim semantics are hardened.

### Workers

Workers are the main horizontal scaling unit.

Scale pattern:

- one queue
- many worker replicas
- shared Redis backend

The first Docker target is:

- `xuanwu-jobs-platform-worker=1`

and the supported scale path is:

- `xuanwu-jobs-platform-worker=N`

## Implementation Notes

- use ARQ because the current repository is already async Python heavy
- keep code layout parallel to the other Python services
- do not embed schedule truth into `xuanwu-jobs`
- do not add fake local `XuanWu` execution

## Verification Target

The completion bar for this phase is:

- `xuanwu-jobs` starts locally
- scheduler can enqueue a due platform job
- worker can consume the queued platform job
- Docker Compose includes Redis and jobs services
- worker replica count can be increased without code changes
