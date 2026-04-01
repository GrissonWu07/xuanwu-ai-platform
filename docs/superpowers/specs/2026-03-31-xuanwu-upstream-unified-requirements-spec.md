# XuanWu Upstream Unified Requirements Spec

Date: 2026-03-31

## Purpose

This is the single upstream requirements document for everything that must be implemented in `XuanWu`.

This repository should no longer spread `XuanWu` requirements across multiple local implementation decisions.

Use this file as the one source of truth for:

- Agent-domain management APIs
- Agent execution APIs
- workflow and knowledge execution ownership
- upstream job execution responsibilities

## Ownership Boundary

`XuanWu` is the only owner of:

- `Agent`
- `Model Provider`
- `Model Config`
- `Knowledge`
- `Workflow`
- Prompt / Template / Feature / MCP style Agent-domain resources
- Agent execution logic
- workflow execution logic
- natural-language-to-schedule intent parsing
- Agent-side planning for device actions

This repository must not create a second source of truth for those domains.

## Required Management APIs

These APIs are required so `xuanwu-management-server` can provide proxy management surfaces in `xuanwu-portal`.

### Agents

- `GET /xuanwu/v1/admin/agents`
- `POST /xuanwu/v1/admin/agents`
- `GET /xuanwu/v1/admin/agents/{agent_id}`
- `PUT /xuanwu/v1/admin/agents/{agent_id}`
- `DELETE /xuanwu/v1/admin/agents/{agent_id}`

### Model Providers

- `GET /xuanwu/v1/admin/model-providers`
- `POST /xuanwu/v1/admin/model-providers`
- `GET /xuanwu/v1/admin/model-providers/{provider_id}`
- `PUT /xuanwu/v1/admin/model-providers/{provider_id}`
- `DELETE /xuanwu/v1/admin/model-providers/{provider_id}`

### Model Configs

- `GET /xuanwu/v1/admin/models`
- `POST /xuanwu/v1/admin/models`
- `GET /xuanwu/v1/admin/models/{model_id}`
- `PUT /xuanwu/v1/admin/models/{model_id}`
- `DELETE /xuanwu/v1/admin/models/{model_id}`

### Knowledge

- `GET /xuanwu/v1/admin/knowledge-bases`
- `POST /xuanwu/v1/admin/knowledge-bases`
- `GET /xuanwu/v1/admin/knowledge-bases/{knowledge_id}`
- `PUT /xuanwu/v1/admin/knowledge-bases/{knowledge_id}`
- `DELETE /xuanwu/v1/admin/knowledge-bases/{knowledge_id}`

### Workflows

- `GET /xuanwu/v1/admin/workflows`
- `POST /xuanwu/v1/admin/workflows`
- `GET /xuanwu/v1/admin/workflows/{workflow_id}`
- `PUT /xuanwu/v1/admin/workflows/{workflow_id}`
- `DELETE /xuanwu/v1/admin/workflows/{workflow_id}`

## Required Runtime APIs

### Agent Runtime Resolve

- `POST /xuanwu/v1/runtime/agents/{agent_id}:resolve`

Purpose:

- return the runtime-ready agent view
- return model, knowledge, workflow, and policy bindings

### Device Command Planning

- `POST /xuanwu/v1/runtime/device-commands:plan`

Purpose:

- convert Agent intent into a standard device-command plan

### Device Command Execution

- `POST /xuanwu/v1/runtime/device-commands:execute`

Purpose:

- accept a standard device-command plan and route it into the local platform execution chain

### Event and Telemetry Ingest

- `POST /xuanwu/v1/runtime/events:ingest`
- `POST /xuanwu/v1/runtime/telemetry:ingest`

Purpose:

- let `XuanWu` consume platform-standardized events and telemetry for Agent reasoning

## Required Job Execution APIs

`XuanWu` must provide execution endpoints so `xuanwu-jobs` can dispatch Agent-domain jobs without embedding Agent logic locally.

Minimum required endpoint:

- `POST /xuanwu/v1/jobs:execute`

Minimum request shape:

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

Minimum response shape:

```json
{
  "status": "completed",
  "result": {
    "summary": "..."
  },
  "events": [],
  "telemetry": []
}
```

This repository should treat `XuanWu` as the execution owner for:

- `agent_run`
- `workflow_run`
- `agent_summary`
- `agent_report`
- natural-language-created scheduled Agent tasks

## Natural Language Schedule Rule

If a user message implies a schedule:

1. `XuanWu` parses the utterance into a schedule draft
2. `xuanwu-management-server` stores the schedule as the platform source of truth
3. `xuanwu-jobs` triggers due schedules
4. `XuanWu` executes Agent-domain jobs through its job execution API

`XuanWu` owns the interpretation.  
This repository owns the stored schedule and dispatch lifecycle.

## Device Invocation Rule

`XuanWu` must not own southbound protocol execution.

The required path is:

1. `XuanWu` decides what should happen
2. `XuanWu` emits a standard device-command plan
3. local platform routes that plan to `xuanwu-iot-gateway`
4. execution result flows back into the local platform
5. platform-standard events and telemetry are optionally re-ingested by `XuanWu`

## Service-to-Service Contract

Every management or execution request from this repository to `XuanWu` must support:

- `X-Xuanwu-Control-Plane-Secret`
- `X-Request-Id`
- `X-Trace-Id`

Expected status handling:

- `200` / `201` success
- `400` malformed request
- `401` authentication failure
- `404` missing resource
- `409` conflict
- `422` business validation failure
- `500` internal error

Unified response recommendation:

```json
{
  "ok": true,
  "data": {}
}
```

Error response recommendation:

```json
{
  "ok": false,
  "error": {
    "code": "resource_conflict",
    "message": "Agent is still bound to active devices",
    "details": {}
  }
}
```

## Required Runtime Views

`XuanWu` should be able to return at least:

### `AgentRuntimeView`

- `agent_id`
- `status`
- `model_provider_id`
- `model_config_id`
- `knowledge_ids`
- `workflow_ids`
- `execution_policy`
- `device_command_policy`
- `feature_flags`

### `DeviceCommandPlan`

- `command_id`
- `trace_id`
- `agent_id`
- `target_device_id`
- `capability_code`
- `action_name`
- `arguments`
- `priority`
- `timeout_ms`

## Local Expectations

This repository will:

- proxy management APIs through `xuanwu-management-server`
- keep schedule truth locally
- keep users, devices, channels, mappings, telemetry, events, alarms, and jobs locally
- avoid reimplementing Agent reasoning or workflow execution

This repository will not:

- create another Agent truth store
- create another Agent scheduler
- create local workflow execution that competes with `XuanWu`

## Superseded Local Documents

This unified spec replaces the need to mentally combine:

- `2026-03-30-xuanwu-agent-domain-api-contract-spec.md`
- `2026-03-31-xuanwu-agent-worker-requirements-spec.md`
- `2026-03-28-xuanwu-upstream-gap-requirements.md`

Those files may still remain for historical traceability, but this file should be treated as the primary upstream requirements source going forward.

## Acceptance Criteria

This upstream contract is satisfied when:

- `xuanwu-management-server` can proxy live Agent, provider, and model CRUD through `XuanWu`
- `xuanwu-jobs` can dispatch Agent-domain jobs to `XuanWu`
- `XuanWu` consumes platform-standard events and telemetry
- `XuanWu` emits standard device-command plans instead of embedding southbound protocol execution
- the local platform no longer needs compatibility logic for missing Agent-domain behavior
