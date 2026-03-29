# Xuanwu Management Server Replacement Design

## Goal

Replace the legacy Java management stack with a Python-first management service named `main/xuanwu-management-server`, while keeping `main/xuanwu-device-server` focused on runtime and device execution only.

## Final Module Boundaries

### `main/xuanwu-device-server`

Owns runtime-only responsibilities:

- device access
- websocket/audio pipeline
- runtime API
- OTA download and upgrade execution
- local tool execution
- vision/runtime execution surfaces

Must not own:

- admin UI
- admin CRUD
- management authentication
- management persistence
- legacy Java-compatible management entrypoints

### `main/xuanwu-management-server`

Owns all management responsibilities:

- admin UI
- admin-facing REST API
- login, auth, permission, audit
- server config
- device config
- bind / unbind
- OTA metadata management
- params / dict / server-side management
- pass-through integration to `XuanWu`
- placeholder pages for reserved domains

### `XuanWu`

Owns the source of truth for:

- `Agent`
- `Model Provider`
- `Model Config`

The management server must proxy those domains and must not persist local copies.

## Current Repository Reality

The target architecture is not in place yet.

Current state:

- `main/xuanwu-device-server` still hosts `/control-plane/v1/*`
- `main/xuanwu-management-server` does not exist yet
- `main/manager-api` and `main/manager-web` are still the legacy reference implementations

This means the replacement work must start by extracting the embedded control-plane from `xuanwu-device-server` into a new standalone Python service.

## Migration Strategy

### Stage 1: Create `main/xuanwu-management-server`

Build a standalone Python service that initially hosts the exact management endpoints currently embedded in `main/xuanwu-device-server`.

Initial extracted domains:

- `GET/PUT /control-plane/v1/config/server`
- `GET/PUT /control-plane/v1/devices/{device_id}`
- `GET/PUT /control-plane/v1/agents/{agent_id}`
- `POST /control-plane/v1/runtime/device-config:resolve`

This stage is about changing the host boundary, not expanding features yet.

### Stage 2: Move Management Ownership Out of `xuanwu-device-server`

After extraction:

- remove `/control-plane/v1/*` routes from `main/xuanwu-device-server`
- move control-plane tests to `main/xuanwu-management-server`
- keep runtime, OTA download, and vision routes in `xuanwu-device-server`

### Stage 3: Replace Legacy Java Management Domains

Implement the first management domains directly in `xuanwu-management-server`:

- login skeleton
- user / role skeleton
- device management
- OTA management
- params management
- dict management
- server-side management

At the same time, add `XuanWu` pass-through domains:

- `/control-plane/v1/xuanwu/agents`
- `/control-plane/v1/xuanwu/model-providers`
- `/control-plane/v1/xuanwu/models`

### Stage 4: Replace Legacy Web Entry

Create the new management UI in `xuanwu-management-server`.

First real pages:

- login
- device management
- agent management
- provider management
- model config
- OTA management
- params management
- dict management
- server-side management
- user / role skeleton

First placeholder pages:

- template
- feature
- MCP
- knowledge / RAG
- prompt / workflow

`Skill` must be display-only if exposed. No install path is allowed.

## Legacy Mapping

### First batch from `main/manager-api`

- `LoginController`
- `DeviceController`
- `ConfigController`
- `OTAController`
- `OTAMagController`
- `SysParamsController`
- `SysDictDataController`
- `SysDictTypeController`
- `ServerSideManageController`

### First batch from `main/manager-web`

- `login.vue`
- `DeviceManagement.vue`
- `ModelConfig.vue`
- `ProviderManagement.vue`
- `OtaManagement.vue`
- `ParamsManagement.vue`
- `DictManagement.vue`
- `ServerSideManager.vue`
- `UserManagement.vue`
- `roleConfig.vue`

The first real `Agent` page must also be added to the new management server even though legacy web does not map it as a standalone first-class domain in this repository state. It is required by the `XuanWu` integration boundary.

## Service-to-Service Integration

`xuanwu-management-server -> XuanWu` must send:

- `X-Xuanwu-Control-Plane-Secret`
- `X-Request-Id`

It must proxy and normalize:

- `400`
- `401`
- `404`
- `409`
- `422`
- `500`

No local truth is allowed for `Agent`, `Model Provider`, or `Model Config`.

## Deployment Target

The target runtime deployment becomes:

- `xuanwu-device-server`
- `xuanwu-management-server`
- `XuanWu`

Legacy Java services remain only as temporary reference implementations until their domains are replaced.

## Acceptance Criteria

This replacement is complete only when all are true:

- `main/xuanwu-management-server` exists and runs independently
- `main/xuanwu-device-server` no longer hosts `/control-plane/v1/*`
- management UI and admin API use `xuanwu-management-server`
- `Agent`, `Model Provider`, and `Model Config` are managed only through `xuanwu-management-server` and proxied to `XuanWu`
- `manager-api` and `manager-web` are no longer the primary management entrypoints
- runtime behavior in `xuanwu-device-server` remains intact
