# XuanWu AI Agent API Spec

## Goal

Define the single upstream contract that `XuanWu AI Agent` must implement for this repository.

This file is the code-aligned contract for:

- management proxy APIs exposed by `xuanwu-management-server`
- portal-facing Agent resource shapes used by `xuanwu-portal`
- runtime planning and execution APIs required by the local platform
- Agent-domain job execution required by `xuanwu-jobs`

## Current Code Alignment

The current repository already depends on `XuanWu` through:

- `main/xuanwu-management-server/core/clients/xuanwu_client.py`
- `main/xuanwu-management-server/core/api/xuanwu_proxy_handler.py`
- `main/xuanwu-management-server/core/http_server.py`
- `main/xuanwu-portal/src/api/management.ts`

Today, the active portal pages directly depend on these proxied collections:

- `GET /control-plane/v1/xuanwu/agents`
- `GET /control-plane/v1/xuanwu/model-providers`
- `GET /control-plane/v1/xuanwu/models`

The local codebase also already defines upstream expectations for:

- `knowledge-bases`
- `workflows`
- runtime agent resolve
- device-command planning
- device-command execution
- event and telemetry ingest
- job execution

This spec consolidates those expectations into one implementation contract.

## Ownership Boundary

`XuanWu AI Agent` is the only source of truth for:

- Agents
- Model providers
- Model configs
- Knowledge bases
- Workflows
- Agent-side prompts, templates, features, and tool definitions
- Agent reasoning and execution
- natural-language-to-schedule parsing
- device-command planning

This repository remains the source of truth for:

- users
- channels
- managed devices
- discovered devices
- device / channel / agent mappings
- telemetry, events, alarms, OTA
- local schedules and job records

## Transport and Authentication

All requests from this repository to `XuanWu` must support:

- `X-Xuanwu-Control-Plane-Secret`
- `X-Request-Id`
- `X-Trace-Id` when available

Current code already sends:

- `X-Xuanwu-Control-Plane-Secret`
- `X-Request-Id`

Recommended response envelope:

```json
{
  "ok": true,
  "data": {}
}
```

Recommended error envelope:

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

Expected status codes:

- `200` success
- `201` created
- `204` deleted / no-content success
- `400` malformed request
- `401` authentication failure
- `404` missing resource
- `409` conflict
- `422` business validation failure
- `500` internal error

## Admin Management APIs

These APIs are the upstream truth that `xuanwu-management-server` proxies for `xuanwu-portal`.

### Agents

- `GET /xuanwu/v1/admin/agents`
- `POST /xuanwu/v1/admin/agents`
- `GET /xuanwu/v1/admin/agents/{agent_id}`
- `PUT /xuanwu/v1/admin/agents/{agent_id}`
- `DELETE /xuanwu/v1/admin/agents/{agent_id}`

List response:

```json
{
  "items": [
    {
      "agent_id": "agent-001",
      "name": "Factory Assistant",
      "status": "active",
      "provider_id": "provider-openai",
      "model_id": "model-gpt-5.4",
      "updated_at": "2026-04-02T10:00:00Z"
    }
  ]
}
```

Detail response:

```json
{
  "agent_id": "agent-001",
  "name": "Factory Assistant",
  "status": "active",
  "description": "Agent for anomaly analysis and device action planning",
  "provider_id": "provider-openai",
  "model_id": "model-gpt-5.4",
  "system_prompt": "...",
  "feature_flags": {
    "device_planning": true,
    "event_reasoning": true
  },
  "updated_at": "2026-04-02T10:00:00Z"
}
```

### Model Providers

- `GET /xuanwu/v1/admin/model-providers`
- `POST /xuanwu/v1/admin/model-providers`
- `GET /xuanwu/v1/admin/model-providers/{provider_id}`
- `PUT /xuanwu/v1/admin/model-providers/{provider_id}`
- `DELETE /xuanwu/v1/admin/model-providers/{provider_id}`

List response:

```json
{
  "items": [
    {
      "provider_id": "provider-openai",
      "name": "OpenAI",
      "provider_type": "openai",
      "status": "active",
      "base_url": "https://api.openai.com/v1"
    }
  ]
}
```

Detail response:

```json
{
  "provider_id": "provider-openai",
  "name": "OpenAI",
  "provider_type": "openai",
  "status": "active",
  "base_url": "https://api.openai.com/v1",
  "capabilities": ["chat", "reasoning", "tools"]
}
```

### Model Configs

- `GET /xuanwu/v1/admin/models`
- `POST /xuanwu/v1/admin/models`
- `GET /xuanwu/v1/admin/models/{model_id}`
- `PUT /xuanwu/v1/admin/models/{model_id}`
- `DELETE /xuanwu/v1/admin/models/{model_id}`

List response:

```json
{
  "items": [
    {
      "model_id": "model-gpt-5.4",
      "label": "GPT-5.4",
      "model_name": "gpt-5.4",
      "provider_id": "provider-openai",
      "status": "active",
      "capabilities": ["chat", "reasoning", "tools"]
    }
  ]
}
```

Detail response:

```json
{
  "model_id": "model-gpt-5.4",
  "label": "GPT-5.4",
  "model_name": "gpt-5.4",
  "provider_id": "provider-openai",
  "status": "active",
  "capabilities": ["chat", "reasoning", "tools"],
  "context_window": 200000,
  "default_temperature": 0.2
}
```

### Knowledge Bases

- `GET /xuanwu/v1/admin/knowledge-bases`
- `POST /xuanwu/v1/admin/knowledge-bases`
- `GET /xuanwu/v1/admin/knowledge-bases/{knowledge_id}`
- `PUT /xuanwu/v1/admin/knowledge-bases/{knowledge_id}`
- `DELETE /xuanwu/v1/admin/knowledge-bases/{knowledge_id}`

List response:

```json
{
  "items": [
    {
      "knowledge_id": "kb-001",
      "name": "Plant Knowledge",
      "status": "active",
      "document_count": 42,
      "updated_at": "2026-04-02T10:00:00Z"
    }
  ]
}
```

Detail response:

```json
{
  "knowledge_id": "kb-001",
  "name": "Plant Knowledge",
  "status": "active",
  "description": "Operations manuals and troubleshooting knowledge",
  "document_count": 42,
  "embedding_provider_id": "provider-openai",
  "updated_at": "2026-04-02T10:00:00Z"
}
```

### Workflows

- `GET /xuanwu/v1/admin/workflows`
- `POST /xuanwu/v1/admin/workflows`
- `GET /xuanwu/v1/admin/workflows/{workflow_id}`
- `PUT /xuanwu/v1/admin/workflows/{workflow_id}`
- `DELETE /xuanwu/v1/admin/workflows/{workflow_id}`

List response:

```json
{
  "items": [
    {
      "workflow_id": "wf-001",
      "name": "Daily Anomaly Review",
      "status": "active",
      "updated_at": "2026-04-02T10:00:00Z"
    }
  ]
}
```

Detail response:

```json
{
  "workflow_id": "wf-001",
  "name": "Daily Anomaly Review",
  "status": "active",
  "description": "Summarize anomalies and propose device actions",
  "version": "1.0.0",
  "updated_at": "2026-04-02T10:00:00Z"
}
```

## Runtime APIs

### Agent Runtime Resolve

- `POST /xuanwu/v1/runtime/agents/{agent_id}:resolve`

Purpose:

- resolve an Agent into runtime-ready execution bindings
- return model, knowledge, workflow, and execution policy references

Request:

```json
{
  "user_id": "user-001",
  "channel_id": "channel-001",
  "device_id": "device-001",
  "trace_id": "trace-001"
}
```

Response:

```json
{
  "agent_id": "agent-001",
  "status": "active",
  "model_provider_id": "provider-openai",
  "model_config_id": "model-gpt-5.4",
  "knowledge_ids": ["kb-001"],
  "workflow_ids": ["wf-001"],
  "execution_policy": {
    "max_tool_calls": 8
  },
  "device_command_policy": {
    "allow_execute": true,
    "require_confirmation": false
  },
  "feature_flags": {
    "device_planning": true
  }
}
```

### Device Command Planning

- `POST /xuanwu/v1/runtime/device-commands:plan`

Purpose:

- convert Agent intent into a platform-standard device-command plan

Request:

```json
{
  "trace_id": "trace-001",
  "agent_id": "agent-001",
  "user_id": "user-001",
  "channel_id": "channel-001",
  "intent": {
    "goal": "Turn off all second-floor lights at 22:00",
    "input_text": "Tonight at 10 PM turn off all second-floor lights"
  },
  "candidate_devices": [
    {
      "device_id": "device-light-001",
      "capabilities": ["power.switch"]
    }
  ]
}
```

Response:

```json
{
  "plan_id": "plan-001",
  "trace_id": "trace-001",
  "agent_id": "agent-001",
  "commands": [
    {
      "command_id": "cmd-001",
      "target_device_id": "device-light-001",
      "capability_code": "power.switch",
      "action_name": "turn_off",
      "arguments": {},
      "priority": "normal",
      "timeout_ms": 10000
    }
  ]
}
```

### Device Command Execution

- `POST /xuanwu/v1/runtime/device-commands:execute`

Purpose:

- accept a standard plan and execute through the local platform path
- `XuanWu` must not embed southbound protocol logic

Request:

```json
{
  "plan_id": "plan-001",
  "trace_id": "trace-001",
  "agent_id": "agent-001",
  "commands": [
    {
      "command_id": "cmd-001",
      "target_device_id": "device-light-001",
      "capability_code": "power.switch",
      "action_name": "turn_off",
      "arguments": {}
    }
  ]
}
```

Response:

```json
{
  "status": "accepted",
  "trace_id": "trace-001",
  "dispatch_count": 1
}
```

### Event Ingest

- `POST /xuanwu/v1/runtime/events:ingest`

Request:

```json
{
  "items": [
    {
      "event_id": "evt-001",
      "event_type": "alarm.triggered",
      "device_id": "device-001",
      "gateway_id": "gw-001",
      "occurred_at": "2026-04-02T10:00:00Z",
      "payload": {
        "severity": "high"
      }
    }
  ]
}
```

Response:

```json
{
  "accepted": 1
}
```

### Telemetry Ingest

- `POST /xuanwu/v1/runtime/telemetry:ingest`

Request:

```json
{
  "items": [
    {
      "telemetry_id": "tm-001",
      "device_id": "device-001",
      "capability_code": "temperature.read",
      "value": 26.3,
      "reported_at": "2026-04-02T10:00:00Z"
    }
  ]
}
```

Response:

```json
{
  "accepted": 1
}
```

## Job Execution API

`xuanwu-jobs` expects `XuanWu` to own Agent-domain execution.

- `POST /xuanwu/v1/jobs:execute`

Request:

```json
{
  "job_run_id": "run-agent-001",
  "schedule_id": "sched-agent-001",
  "job_type": "agent_run",
  "executor_type": "agent",
  "target_id": "agent-001",
  "scheduled_for": "2026-04-02T10:00:00Z",
  "payload": {
    "user_id": "user-001",
    "channel_id": "channel-001",
    "device_id": "device-001",
    "input_text": "Summarize yesterday anomalies"
  }
}
```

Response:

```json
{
  "status": "completed",
  "result": {
    "summary": "Three devices reported high temperature anomalies."
  },
  "events": [],
  "telemetry": []
}
```

`job_type` values that must be supported by `XuanWu`:

- `agent_run`
- `workflow_run`
- `agent_summary`
- `agent_report`

## Portal and Proxy Shape Contract

The current portal code expects these exact collection shapes.

### Agent list item

```json
{
  "agent_id": "agent-001",
  "name": "Factory Assistant",
  "status": "active",
  "provider_id": "provider-openai",
  "model_id": "model-gpt-5.4",
  "updated_at": "2026-04-02T10:00:00Z"
}
```

### Model provider item

```json
{
  "provider_id": "provider-openai",
  "name": "OpenAI",
  "provider_type": "openai",
  "status": "active",
  "base_url": "https://api.openai.com/v1"
}
```

### Model config item

```json
{
  "model_id": "model-gpt-5.4",
  "label": "GPT-5.4",
  "model_name": "gpt-5.4",
  "provider_id": "provider-openai",
  "status": "active",
  "capabilities": ["chat", "reasoning", "tools"]
}
```

These list endpoints should return:

```json
{
  "items": []
}
```

without wrapping them under `data.items`, because `xuanwu-management-server` currently forwards upstream payloads directly.

## Local-to-Upstream Mapping Rule

`xuanwu-management-server` remains the owner of:

- `device-agent` mappings
- `agent-model-provider` mappings
- `agent-model-config` mappings
- `agent-knowledge` mappings
- `agent-workflow` mappings

`XuanWu` remains the owner of the actual resource objects behind those IDs.

This means:

- local platform stores relationship edges
- `XuanWu` stores Agent-domain resource truth
- runtime resolve APIs are responsible for turning both sides into an executable view

## Minimum Acceptance Criteria

This contract is complete when:

- `xuanwu-management-server` can proxy live CRUD for agents, model providers, and model configs
- `XuanWu` also exposes live CRUD for knowledge bases and workflows
- `xuanwu-portal` can render the current `Agents` and `AI Config Proxy` pages from live upstream data
- `xuanwu-jobs` can dispatch Agent-domain jobs through `/xuanwu/v1/jobs:execute`
- `XuanWu` can resolve runtime Agent bindings and produce platform-standard device-command plans
- `XuanWu` can ingest platform-standard events and telemetry for reasoning

## Relationship To Older Specs

This document is the recommended handoff spec for the `XuanWu` implementation thread.

It consolidates and aligns:

- `2026-03-30-xuanwu-agent-domain-api-contract-spec.md`
- `2026-03-31-xuanwu-upstream-unified-requirements-spec.md`
- `2026-03-31-xuanwu-agent-worker-requirements-spec.md`

Those files remain useful historical references, but this file is the most code-aligned upstream contract for current implementation work.
