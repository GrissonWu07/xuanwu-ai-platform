# XuanWu Agent Worker Requirements Spec

## Goal

Define the worker responsibilities that belong to upstream `XuanWu`, so this repository can stay aligned to the API contract without reimplementing Agent-domain execution locally.

## Ownership Boundary

`XuanWu` owns:

- `xuanwu-agent-worker`
- `xuanwu-workflow-worker`
- all Agent reasoning, planning, and workflow execution
- all Model / Knowledge / Workflow truth
- all natural-language-to-schedule intent parsing
- all decisions that turn user intent into standard device-command plans

This repository does **not** implement those workers. It only defines the contract and prepares the local worker topology around them.

## Required Worker Classes

### 1. `xuanwu-agent-worker`

Consumes queue:

- `agent`

Executes:

- `agent_run`
- `agent_report`
- `agent_summary`
- other Agent-domain jobs that require model inference

Job payload minimum:

```json
{
  "job_run_id": "run-agent-001",
  "schedule_id": "sched-agent-001",
  "job_type": "agent_run",
  "executor_type": "agent",
  "target_id": "agent-001",
  "scheduled_for": "2026-03-31T10:00:00Z",
  "payload": {
    "user_id": "user-001",
    "channel_id": "channel-001",
    "device_id": "device-001",
    "input_text": "Summarize yesterday anomalies"
  }
}
```

### 2. `xuanwu-workflow-worker`

Consumes queue:

- `agent`

Executes:

- `workflow_run`
- delayed workflow branches
- workflow retries and continuation steps

Job payload minimum:

```json
{
  "job_run_id": "run-workflow-001",
  "schedule_id": "sched-workflow-001",
  "job_type": "workflow_run",
  "executor_type": "agent",
  "target_id": "workflow-001",
  "scheduled_for": "2026-03-31T10:00:00Z",
  "payload": {
    "agent_id": "agent-001",
    "workflow_id": "workflow-001",
    "trigger_source": "schedule"
  }
}
```

## Required Runtime Contract

`XuanWu` workers must accept jobs from Redis/ARQ and must report execution state back to `xuanwu-management-server`.

### Completion callback

- `POST /control-plane/v1/jobs/runs/{job_run_id}:complete`

### Failure callback

- `POST /control-plane/v1/jobs/runs/{job_run_id}:fail`

### Required request headers

- `X-Xuanwu-Control-Secret`
- `X-Request-Id`

## Required Upstream APIs

The local platform assumes `XuanWu` exposes:

- `POST /xuanwu/v1/runtime/agents/{agent_id}:resolve`
- `POST /xuanwu/v1/runtime/device-commands:plan`
- `POST /xuanwu/v1/runtime/device-commands:execute`
- `POST /xuanwu/v1/runtime/events:ingest`
- `POST /xuanwu/v1/runtime/telemetry:ingest`

## Device Invocation Rule

`XuanWu` workers must not embed southbound protocol logic.

The required path is:

1. `xuanwu-agent-worker` or `xuanwu-workflow-worker` decides what should happen
2. `XuanWu` emits a standard device-command plan
3. `xuanwu-iot-gateway` executes the actual southbound command through its execution API
4. execution results flow back to `xuanwu-management-server`

## Schedule Rule

If a schedule originates from natural language:

1. `XuanWu` parses the user utterance into a schedule draft
2. `xuanwu-management-server` stores the schedule as the source of truth
3. `xuanwu-jobs` triggers it when due
4. `xuanwu-agent-worker` or `xuanwu-workflow-worker` executes it

## Scaling Rule

`XuanWu` workers should scale horizontally by queue consumer replica count.

Recommended topology:

- `xuanwu-agent-worker` x N
- `xuanwu-workflow-worker` x M

Both consume the `agent` queue but should enforce:

- per-agent concurrency limits
- per-user concurrency limits
- idempotent `job_run_id`
- explicit timeout and retry policy

## Non-Goals For This Repository

This repository should not:

- reimplement `xuanwu-agent-worker`
- reimplement workflow execution
- create a second Agent scheduler
- create a second Agent truth store

## Conclusion

All Agent-domain worker execution belongs to upstream `XuanWu`.

This repository should only:

- define the job contract
- provide local worker classes for `management`, `gateway`, and `device`
- integrate with `XuanWu` through API and queue contracts
