# XuanWu Upstream Gap Requirements

## Purpose

This document records the `XuanWu` changes that `ai-assist-device` still depends on, without blocking the local Python refactor. `xuanwu-device-server` and `xuanwu-management-server` now assume `XuanWu` is the only source of truth for agent-management objects.

## Required Admin APIs

`XuanWu` must provide these management endpoints for `xuanwu-management-server` to proxy:

- `GET /xuanwu/v1/admin/agents`
- `POST /xuanwu/v1/admin/agents`
- `GET /xuanwu/v1/admin/agents/{agent_id}`
- `PUT /xuanwu/v1/admin/agents/{agent_id}`
- `DELETE /xuanwu/v1/admin/agents/{agent_id}`
- `GET /xuanwu/v1/admin/model-providers`
- `POST /xuanwu/v1/admin/model-providers`
- `GET /xuanwu/v1/admin/model-providers/{provider_id}`
- `PUT /xuanwu/v1/admin/model-providers/{provider_id}`
- `DELETE /xuanwu/v1/admin/model-providers/{provider_id}`
- `GET /xuanwu/v1/admin/models`
- `POST /xuanwu/v1/admin/models`
- `GET /xuanwu/v1/admin/models/{model_id}`
- `PUT /xuanwu/v1/admin/models/{model_id}`
- `DELETE /xuanwu/v1/admin/models/{model_id}`

## Service-to-Service Contract

Every proxied request from `xuanwu-management-server` must support:

- `X-Xuanwu-Control-Plane-Secret`
- `X-Request-Id`

Expected status handling:

- `200` / `201` for success
- `400` for malformed requests
- `401` for authentication failure
- `404` for missing resources
- `409` for reference conflicts
- `422` for business validation errors
- `500` for internal failures

## Expected Object Scope

`XuanWu` owns real persistence and validation for:

- `Agent`
- `Model Provider`
- `Model Config`

`xuanwu-management-server` only proxies those objects and must not keep a second source of truth.

## Non-Blocking Local Ownership

The following capabilities are intentionally handled locally in `xuanwu-management-server` for now and do not block this repository:

- `/control-plane/v1/chat-history/report`
- `/control-plane/v1/chat-summaries/{summary_id}:generate`

If `XuanWu` later needs to own those resources, a follow-up migration can move storage ownership without changing the current `xuanwu-device-server` runtime boundary.
