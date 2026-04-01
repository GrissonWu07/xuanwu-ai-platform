# PostgreSQL Persistence Design

## Purpose

This spec defines the persistence redesign for the local platform layer so that:

- `xuanwu-management-server` no longer uses YAML files as its primary source of truth
- `xuanwu-iot-gateway` no longer keeps durable device state only in memory
- root Docker deployment starts PostgreSQL as a default platform dependency
- the local platform has a production-oriented persistence baseline before upstream `XuanWu` integration is finalized

The scope of this spec is limited to repository-local services:

- `xuanwu-management-server`
- `xuanwu-jobs`
- `xuanwu-iot-gateway`
- root deployment assets

It explicitly does not migrate:

- `xuanwu-device-gateway` local bootstrap configuration
- `xuanwu-device-gateway` local short memory file
- upstream `XuanWu` domain data

## Decision Summary

The platform will move from a file-based control-plane store to PostgreSQL with SQLAlchemy ORM.

The database layout is:

- one PostgreSQL instance
- schema `xw_mgmt` for `xuanwu-management-server`
- schema `xw_iot` for `xuanwu-iot-gateway`

The architecture rule is:

- platform business truth belongs in `xw_mgmt`
- gateway runtime state belongs in `xw_iot`
- `xuanwu-jobs` continues to use management-owned schedules and job runs instead of inventing a separate truth

This means PostgreSQL becomes the only durable truth for:

- devices
- discovered devices
- users
- channels
- mappings
- gateway records
- events
- telemetry
- alarms
- OTA metadata
- schedules
- job runs
- command results
- device state shadow in the IoT gateway

YAML storage remains only for:

- `xuanwu-device-gateway` bootstrap overrides
- `xuanwu-device-gateway` local short memory
- one-time import source for old management YAML data

## Design Goals

The persistence redesign must achieve all of the following:

1. Preserve the current platform behavior and API contract as much as possible.
2. Replace YAML truth with relational storage without introducing long-term dual-write complexity.
3. Keep service boundaries clear:
   - management owns platform truth
   - iot gateway owns runtime state shadow
   - jobs operates on management truth
4. Make root Docker deployment self-contained by starting PostgreSQL by default.
5. Support migration from the existing YAML store through a one-time import path.

## Non-Goals

This spec does not include:

- upstream `XuanWu` data persistence
- Redis introduction
- multi-database sharding
- event streaming infrastructure
- replacing `xuanwu-device-gateway` bootstrap files with database-backed runtime config
- a full Alembic-based migration system in the first delivery

## Service Ownership

### `xuanwu-management-server`

Owns durable business truth in PostgreSQL schema `xw_mgmt`.

It is responsible for:

- users
- roles
- channels
- devices
- discovered devices
- gateways
- all mapping models
- events
- telemetry
- alarms
- firmware metadata
- OTA campaigns
- auth sessions
- command results
- chat history
- chat summaries
- job schedules
- job runs
- dashboard read models assembled from those records

It does not own:

- protocol execution
- MQTT broker lifecycle
- gateway-local runtime shadow
- `xuanwu-device-gateway` local bootstrap and local memory files

### `xuanwu-jobs`

Does not become its own persistence truth.

It continues to:

- read due schedules from `xuanwu-management-server`
- claim and execute job runs through `xuanwu-management-server`
- rely on management-side schedule and run storage in `xw_mgmt`

That means jobs persistence is logically owned by management even when jobs drives execution.

### `xuanwu-iot-gateway`

Owns runtime-oriented gateway state in PostgreSQL schema `xw_iot`.

It is responsible for durable storage of:

- latest per-device gateway state shadow
- last command metadata relevant to gateway runtime
- last adapter presence
- last bridge presence
- gateway-local observed device runtime shape when it is not yet aggregated into management read models

It does not own:

- formal managed device truth
- lifecycle and claim/bind truth
- alert truth
- schedule truth

### `xuanwu-device-gateway`

Remains file-backed for local bootstrap and local short memory:

- `deploy/data/device-gateway/.config.yaml`
- `deploy/data/device-gateway/.memory.yaml`

It stays out of this first PostgreSQL migration.

## PostgreSQL Layout

### Instance

Root deployment starts one PostgreSQL instance for the whole local platform.

Recommended defaults:

- database: `xuanwu_platform`
- user: `xuanwu`
- password: environment-provided

### Schemas

#### `xw_mgmt`

Tables should cover:

- `server_profile`
- `users`
- `roles`
- `channels`
- `devices`
- `discovered_devices`
- `gateways`
- `user_device_mappings`
- `user_channel_mappings`
- `channel_device_mappings`
- `device_agent_mappings`
- `agent_model_provider_mappings`
- `agent_model_config_mappings`
- `agent_knowledge_mappings`
- `agent_workflow_mappings`
- `events`
- `telemetry`
- `alarms`
- `capabilities`
- `capability_routes`
- `ota_firmwares`
- `ota_campaigns`
- `auth_sessions`
- `command_results`
- `chat_history`
- `chat_summaries`
- `job_schedules`
- `job_runs`

#### `xw_iot`

Tables should cover:

- `device_state`
- `adapter_presence`
- `bridge_presence`

The first delivery can start with `device_state` as the only required table, and add the other two as schema placeholders if the implementation does not yet consume them.

## Repository Structure Changes

### Management server

Add:

- `main/xuanwu-management-server/core/db/`
- `main/xuanwu-management-server/core/db/engine.py`
- `main/xuanwu-management-server/core/db/session.py`
- `main/xuanwu-management-server/core/db/bootstrap.py`
- `main/xuanwu-management-server/core/db/models.py`
- `main/xuanwu-management-server/core/store/base.py`
- `main/xuanwu-management-server/core/store/sqlalchemy_store.py`
- `main/xuanwu-management-server/scripts/import_yaml_control_plane.py`

Keep:

- `main/xuanwu-management-server/core/store/local_store.py`

But change its role to:

- legacy import source
- optional fallback for emergency debugging
- not the default truth in Docker deployment

### IoT gateway

Add:

- `main/xuanwu-iot-gateway/core/db/`
- `main/xuanwu-iot-gateway/core/db/engine.py`
- `main/xuanwu-iot-gateway/core/db/session.py`
- `main/xuanwu-iot-gateway/core/db/bootstrap.py`
- `main/xuanwu-iot-gateway/core/db/models.py`
- `main/xuanwu-iot-gateway/core/state/sqlalchemy_state_store.py`

The current in-memory `device_state` dictionary in `GatewayHandler` will be replaced with a state store abstraction backed by PostgreSQL.

### Root deployment

Add PostgreSQL into:

- `docker-compose.yml`

Add host storage:

- `deploy/postgres/`

Add environment variables into:

- `.env.example`
- deployment docs
- setup script

## Configuration Design

### Root environment variables

Required additions:

- `XUANWU_PG_HOST`
- `XUANWU_PG_PORT`
- `XUANWU_PG_DB`
- `XUANWU_PG_USER`
- `XUANWU_PG_PASSWORD`
- `XUANWU_MGMT_PG_SCHEMA`
- `XUANWU_IOT_PG_SCHEMA`

Recommended default shape:

- `XUANWU_PG_HOST=postgres`
- `XUANWU_PG_PORT=5432`
- `XUANWU_PG_DB=xuanwu_platform`
- `XUANWU_PG_USER=xuanwu`
- `XUANWU_PG_PASSWORD=xuanwu_local_password`
- `XUANWU_MGMT_PG_SCHEMA=xw_mgmt`
- `XUANWU_IOT_PG_SCHEMA=xw_iot`

### Management runtime config

`xuanwu-management-server` must load:

- PostgreSQL connection details
- schema name
- storage backend selector

The default backend in Docker deployment becomes `postgres`.

### IoT gateway config

`xuanwu-iot-gateway` must load:

- PostgreSQL connection details
- schema name

The gateway state layer must write durable `device_state` rows on every relevant command, heartbeat, ingest, and bridge event path.

## Data Model Guidance

### Management tables

The relational design should preserve existing external shapes as JSON-like records, but with normalized identities and indexes.

Recommended model style:

- explicit scalar columns for core query fields
- JSON columns for extensible payloads

Examples:

#### `devices`

Core columns:

- `device_id`
- `user_id`
- `display_name`
- `device_kind`
- `ingress_type`
- `gateway_id`
- `protocol_type`
- `adapter_type`
- `runtime_endpoint`
- `bind_status`
- `lifecycle_status`
- `connection_status`
- `session_status`
- `last_seen_at`
- `last_event_at`
- `last_telemetry_at`
- `last_command_at`
- `channel_ids_json`
- `capability_refs_json`
- `runtime_overrides_json`
- `source_payload_json`

#### `discovered_devices`

Core columns:

- `discovery_id`
- `device_id`
- `display_name`
- `ingress_type`
- `device_kind`
- `gateway_id`
- `protocol_type`
- `adapter_type`
- `runtime_endpoint`
- `first_seen_at`
- `last_seen_at`
- `discovery_status`
- `ignore_reason`
- `promoted_device_id`
- `source_payload_json`

#### `events`, `telemetry`, `alarms`

These must keep queryable columns for:

- `device_id`
- `gateway_id`
- type and severity fields
- observed/occurred timestamps

while preserving payload flexibility in JSON columns.

### IoT gateway `device_state`

The current in-memory structure is too light:

- `device_id`
- `last_request_id`
- `last_command_name`
- `status`

The durable table should at least support:

- `device_id`
- `gateway_id`
- `adapter_type`
- `protocol_type`
- `device_kind`
- `status`
- `last_request_id`
- `last_command_name`
- `last_result_json`
- `last_seen_at`
- `updated_at`

This gives the gateway a durable local shadow without turning it into the formal business truth.

## Storage Abstraction

### Management store abstraction

`ControlPlaneHandler` must stop depending on `LocalControlPlaneStore` concretely.

It should depend on a store interface that exposes the current public methods used by handlers.

First delivery goal:

- keep method names stable
- switch constructor wiring from `LocalControlPlaneStore.from_config()` to `SQLAlchemyControlPlaneStore.from_config()`

This limits API churn and makes the migration safer.

### Gateway state abstraction

`GatewayHandler.device_state` must be replaced with a store dependency.

The first abstraction only needs:

- `upsert_device_state(...)`
- `get_device_state(device_id)`

Optional follow-up methods:

- `list_recent_device_state(...)`
- `record_adapter_presence(...)`
- `record_bridge_presence(...)`

## Migration Strategy

The platform should not run long-term YAML and PostgreSQL dual writes.

The migration strategy is:

1. keep YAML store code as legacy source only
2. introduce PostgreSQL-backed store
3. provide a one-time YAML import script
4. switch Docker deployment default to PostgreSQL
5. keep the import utility for old local environments

This avoids ongoing truth divergence.

### Import expectations

The import script should:

- read the old `main/xuanwu-management-server/data/control_plane` tree
- import all supported YAML entities into `xw_mgmt`
- preserve ids and timestamps where present
- be safe to re-run with upsert behavior

## Root Docker Deployment Changes

### PostgreSQL service

The root deployment must start:

- `postgres`

with host-mounted storage under:

- `deploy/postgres/`

### Service wiring

The following services must receive PostgreSQL environment variables:

- `xuanwu-management-server`
- `xuanwu-iot-gateway`

`xuanwu-jobs` does not need direct PostgreSQL access in the first delivery if it continues to use management APIs for all schedule and run interactions.

## API Impact

Public API routes should remain unchanged.

The migration should be persistence-internal for:

- control plane APIs
- jobs APIs
- iot gateway health and device-state APIs

The only externally visible differences should be:

- durable device-state survival across restarts in `xuanwu-iot-gateway`
- more reliable persistence behavior in `xuanwu-management-server`

## Testing Strategy

### Management server

Add:

- PostgreSQL-backed integration tests for store contract behavior
- import tests for YAML-to-PG migration
- handler tests proving APIs still return the same shapes

### IoT gateway

Add:

- persistent `device_state` tests
- command dispatch updates durable state
- ingest updates durable state
- bridge callback updates durable state

### Root deployment

Add:

- tests asserting root Compose includes PostgreSQL
- tests asserting Postgres env variables are documented and wired
- tests asserting host path `deploy/postgres/` exists or is prepared by setup

## Documentation Impact

The following docs must be updated:

- `docs/quick-start.md`
- `docs/Deployment.md`
- `docs/current-platform-capabilities.md`
- `docs/current-api-surfaces.md`
- `docs/platform-delivery-overview.md`

They must stop describing YAML as the primary platform persistence model and instead describe:

- PostgreSQL for platform truth
- host-mounted files only for `xuanwu-device-gateway` bootstrap and local short memory

## Current Status Before Implementation

### Already true

- management truth exists, but in YAML
- jobs truth exists, but in management YAML
- iot gateway runtime state exists, but in memory
- root Docker deployment exists
- `xuanwu-device-gateway` local bootstrap and memory files are already host-exposed

### Not yet true

- PostgreSQL is not part of root deployment
- SQLAlchemy ORM is not present in management or iot gateway
- management truth is not relational
- iot gateway device shadow is not durable
- YAML import tooling does not exist

## Acceptance Criteria

This persistence redesign is complete when:

- root Docker deployment starts PostgreSQL by default
- `xuanwu-management-server` uses PostgreSQL schema `xw_mgmt` as its primary durable truth
- `xuanwu-jobs` schedules and runs continue to work against PostgreSQL-backed management truth
- `xuanwu-iot-gateway` stores device state in PostgreSQL schema `xw_iot`
- iot gateway device state survives process restart
- a one-time import command can migrate old YAML control-plane data into PostgreSQL
- deployment docs and quick start describe PostgreSQL as the default persistence layer
- `xuanwu-device-gateway` local files remain host-mounted and unchanged
