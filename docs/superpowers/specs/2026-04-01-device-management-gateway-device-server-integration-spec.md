# Device Management, Gateway, and Device-Server Integration Spec

## Purpose

This spec defines the end-to-end integration model between:

- `xuanwu-management-server`
- `xuanwu-gateway`
- `xuanwu-device-server`

It clarifies:

- ownership boundaries
- data flow
- interaction patterns
- API design
- what is already implemented
- what is still missing

This document is the authoritative local design for device registration, discovery, runtime ingress, and unified device management before `XuanWu`-driven execution is layered on top.

## Design Summary

The platform has two different device ingress paths that must converge into one unified device-management model:

- `xuanwu-device-server` handles conversational devices and runtime session devices
- `xuanwu-gateway` handles IoT, industrial, actuator, and sensor devices

Both paths must converge into `xuanwu-management-server`, which is the only local source of truth for managed devices.

The central design rule is:

- ingress services discover and report devices
- management owns formal device records
- portal reads and operates only on management-owned device state

This means gateway-local caches or device-server runtime session state are never the durable device-management truth.

## Service Responsibilities

### `xuanwu-management-server`

Owns:

- managed device records
- user ownership
- device lifecycle
- device claim and bind
- user-channel-device-agent mappings
- telemetry, event, and alarm truth
- gateway records
- schedule truth
- portal-facing device read models

Does not own:

- raw protocol execution
- runtime WebSocket session handling
- model or agent-domain reasoning

### `xuanwu-gateway`

Owns:

- protocol adapters
- device command execution
- sensor ingest normalization
- industrial protocol access
- gateway-local transient state

Does not own:

- durable managed-device truth
- user ownership
- claim/bind/lifecycle truth

### `xuanwu-device-server`

Owns:

- conversational device ingress
- runtime session handling
- OTA and runtime connection setup
- runtime-side job execution entrypoint
- local session state

Does not own:

- durable managed-device truth
- device ownership
- gateway protocol execution

## Core Entity Model

### Managed Device

The managed-device model must be the normalized record stored in `xuanwu-management-server`.

Required fields:

- `device_id`
- `device_kind`
- `ingress_type`
- `user_id`
- `bind_status`
- `lifecycle_status`
- `gateway_id`
- `protocol_type`
- `adapter_type`
- `runtime_endpoint`
- `channel_ids`
- `capability_refs`
- `runtime_overrides`
- `last_seen_at`
- `last_event_at`
- `last_telemetry_at`
- `last_command_at`

Field intent:

- `device_kind`
  - `conversational`
  - `actuator`
  - `sensor`
  - `industrial`
- `ingress_type`
  - `device_server`
  - `gateway`
- `gateway_id`
  - present when a device is managed through `xuanwu-gateway`
- `runtime_endpoint`
  - present when a device is managed through `xuanwu-device-server`

### Discovered Device

This spec introduces a missing intermediate entity.

`Discovered Device` is not yet a formally managed device. It represents a device observed by ingress services before user ownership and lifecycle are confirmed.

Required fields:

- `discovery_id`
- `device_id`
- `ingress_type`
- `gateway_id`
- `protocol_type`
- `adapter_type`
- `device_kind`
- `source_payload`
- `first_seen_at`
- `last_seen_at`
- `discovery_status`

`discovery_status` values:

- `pending`
- `claimed`
- `ignored`
- `promoted`

This layer is necessary so the platform can safely support:

- gateway-first discovery
- device-server first-contact discovery
- anonymous pre-registration
- later claim/bind into a managed device

## Target Relationship Model

The authoritative ownership model remains:

- `user -> device`

Control surfaces remain:

- `user -> channel -> device`

Execution and reasoning remain:

- `device -> agent`
- `agent -> model provider`
- `agent -> model config`
- `agent -> knowledge`
- `agent -> workflow`

Ingress relationship model:

- `gateway -> discovered_device`
- `device_server -> discovered_device`
- `discovered_device -> managed_device`

## End-to-End Data Flow

### Flow A: Gateway Device Discovery

1. A physical IoT or industrial device is discovered or referenced through a gateway adapter.
2. `xuanwu-gateway` normalizes the identity into:
   - `device_id`
   - `gateway_id`
   - `protocol_type`
   - `adapter_type`
   - `device_kind`
3. `xuanwu-gateway` calls `xuanwu-management-server` discovery API.
4. `xuanwu-management-server` stores or updates a `discovered_device`.
5. Portal shows the device in a `Pending Devices` or equivalent discovery view.
6. User claims or promotes the device into a managed device.
7. Management creates the formal `device` record and links it back to the discovery record.

### Flow B: Conversational Device First Contact

1. A conversational device connects through `xuanwu-device-server`.
2. `xuanwu-device-server` identifies the device and runtime context.
3. If the device is unknown, `xuanwu-device-server` calls management discovery API using `ingress_type=device_server`.
4. Management creates or updates a `discovered_device`.
5. User claims or binds the device.
6. Runtime config resolution then proceeds against the formal managed device record.

### Flow C: Runtime Telemetry/Event Continuation

1. Gateway or device-server emits telemetry, events, or command results.
2. Payloads include `device_id` and ingress metadata.
3. Management stores telemetry/event/alarm data.
4. Management updates device recency fields:
   - `last_seen_at`
   - `last_event_at`
   - `last_telemetry_at`
5. Portal device detail page reads unified state from management.

### Flow D: Device Control

1. Portal or future `XuanWu` execution identifies a managed device.
2. Management resolves routing:
   - if `ingress_type=gateway`, command path is `xuanwu-gateway`
   - if `ingress_type=device_server`, runtime command path is `xuanwu-device-server`
3. Execution result returns through gateway or device-server callback APIs.
4. Management stores command results and mirrors `command.result` event.

## Interaction Model

### Management and Gateway

Current interaction:

- gateway posts telemetry
- gateway posts events
- gateway posts command results

Target interaction:

- gateway also posts device discovery and device-state updates
- management does not infer formal device creation from random telemetry alone
- management explicitly promotes discovered devices into formal managed devices

### Management and Device-Server

Current interaction:

- device-server resolves runtime config from management
- device-server participates in runtime job execution

Target interaction:

- device-server also reports first-contact discovery for unknown devices
- device-server reports runtime presence and online status into management device recency fields
- management becomes the only portal-facing device detail source

### Gateway and Device-Server

These two services should not manage each other directly.

They only converge through:

- shared managed-device truth in management
- shared execution routing resolved by management

## API Design

### Already Existing APIs

#### Management device APIs

Already present:

- `GET /control-plane/v1/devices`
- `POST /control-plane/v1/devices`
- `GET /control-plane/v1/devices/{device_id}`
- `GET /control-plane/v1/devices/{device_id}/detail`
- `PUT /control-plane/v1/devices/{device_id}`
- `POST /control-plane/v1/devices/{device_id}:claim`
- `POST /control-plane/v1/devices/{device_id}:bind`
- `POST /control-plane/v1/devices/{device_id}:suspend`
- `POST /control-plane/v1/devices/{device_id}:retire`
- `POST /control-plane/v1/devices:batch-import`

#### Management gateway APIs

Already present:

- `GET /control-plane/v1/gateways`
- `GET /control-plane/v1/gateways/{gateway_id}`
- `POST /control-plane/v1/gateways`
- `PUT /control-plane/v1/gateways/{gateway_id}`

#### Gateway callback APIs

Already present:

- `POST /control-plane/v1/gateway/events`
- `POST /control-plane/v1/gateway/telemetry`
- `POST /control-plane/v1/gateway/command-results`

### Missing APIs

#### Discovery APIs in management

Required:

- `GET /control-plane/v1/discovered-devices`
- `POST /control-plane/v1/discovered-devices`
- `GET /control-plane/v1/discovered-devices/{discovery_id}`
- `POST /control-plane/v1/discovered-devices/{discovery_id}:promote`
- `POST /control-plane/v1/discovered-devices/{discovery_id}:ignore`

#### Gateway-originated discovery callback

Required:

- `POST /control-plane/v1/gateway/device-discovery`

Payload:

```json
{
  "discovery_id": "disc-gw-001",
  "device_id": "sensor-01",
  "gateway_id": "gateway-sh-01",
  "ingress_type": "gateway",
  "device_kind": "sensor",
  "protocol_type": "mqtt",
  "adapter_type": "sensor_mqtt",
  "source_payload": {
    "topic": "factory/line1/temp/1"
  },
  "first_seen_at": "2026-04-01T08:00:00Z",
  "last_seen_at": "2026-04-01T08:00:00Z"
}
```

#### Device-server-originated discovery callback

Required:

- `POST /control-plane/v1/runtime/device-discovery`

Payload:

```json
{
  "discovery_id": "disc-runtime-001",
  "device_id": "esp32-voice-01",
  "ingress_type": "device_server",
  "device_kind": "conversational",
  "runtime_endpoint": "ws://xuanwu-device-server:8000/xuanwu/v1/",
  "source_payload": {
    "client_id": "esp32-voice-01",
    "firmware_version": "1.2.0"
  },
  "first_seen_at": "2026-04-01T08:00:00Z",
  "last_seen_at": "2026-04-01T08:00:00Z"
}
```

#### Device recency/state update API

Required:

- `POST /control-plane/v1/devices/{device_id}:heartbeat`

Payload:

```json
{
  "ingress_type": "gateway",
  "gateway_id": "gateway-sh-01",
  "status": "online",
  "last_seen_at": "2026-04-01T08:05:00Z",
  "session_status": null
}
```

This API allows both gateway and device-server to update unified device recency and connection state without rewriting the entire device record.

#### Device detail aggregation API expansion

Existing:

- `GET /control-plane/v1/devices/{device_id}/detail`

Still required in response shape:

- formal device record
- related gateway summary
- latest runtime presence
- latest telemetry sample
- latest event
- latest alarm summary
- latest command result
- discovery provenance

## Current Implementation Status

### Completed

#### Device management

Completed:

- formal device CRUD
- device lifecycle
- device claim/bind/suspend/retire
- device batch import
- mapping model integration
- discovered-device store
- discovered-device APIs
- discovered-device promotion and ignore flow
- device heartbeat/update API
- richer device-detail aggregation with provenance and latest operational state

#### Gateway management

Completed:

- gateway CRUD-like upsert and listing
- telemetry ingest
- event ingest
- command-result ingest
- protocol adapter execution
- automatic discovery callback from gateway
- management-side pending-registration flow through discovered devices
- heartbeat and recency updates into managed-device truth

#### Device-server management integration

Completed:

- runtime config resolution through management
- runtime job execution surface
- boundary isolation from management hosting
- first-contact discovery callback from device-server
- automatic anonymous pending-device creation through discovered-device promotion
- runtime-origin presence sync into managed-device truth

#### Unified portal view

Completed:

- pending/discovered device workspace
- visible distinction between:
  - gateway-managed device ingress
  - device-server-managed device ingress
- discovery-to-managed promotion workflow

### Remaining Work

The repository-local work defined by this spec is complete.

What remains is outside this local scope:

- final upstream `XuanWu` execution integration
- live-environment reconciliation policies such as gateway offline/orphan handling under real deployment conditions
- end-to-end validation with physical gateway/device-server ingress sources

## Required Portal Behavior

Portal must ultimately expose:

- `Devices`
  - managed devices
  - discovered devices
  - per-device ingress source
  - lifecycle and bind state
- `Channels & Gateways`
  - gateway inventory
  - related discovered devices
  - related managed devices
- device detail
  - runtime and protocol provenance
  - latest telemetry/events/alerts
  - routing to agent and channel

## Failure and Edge Cases

### Gateway sees a device that management has never seen

Expected behavior:

- create or update discovered-device record
- do not silently invent full managed-device ownership

### Device-server sees a device with no user

Expected behavior:

- create discovered-device record
- if promoted directly, default owner can be `anonymous`

### Gateway goes offline

Expected behavior:

- gateway status changes separately
- managed devices retain truth
- related device operational state may become `degraded` or `unreachable`

### Telemetry arrives for unknown device

Expected behavior:

- accept ingest if source is trusted
- ensure discovered-device record exists
- do not drop useful telemetry solely because claim/bind is not completed

## Acceptance Criteria

This integration area is complete when:

- gateway-discovered devices are visible in management before formal claim
- device-server first-contact devices are visible in management before formal claim
- portal can distinguish discovered vs managed devices
- portal can promote a discovered device into a managed device
- telemetry/event/command-result records update managed-device recency
- device detail shows ingress provenance and latest operational state
- gateway and device-server no longer act as de facto device inventories outside management truth

## Recommended Implementation Order

Implemented locally in this order:

1. Add `discovered_devices` store and APIs to `xuanwu-management-server`
2. Add `gateway device-discovery` callback
3. Add `device-server device-discovery` callback
4. Add `device heartbeat` update API
5. Expand device detail aggregation
6. Add portal discovered-device views and promotion actions
7. Keep gateway offline and orphan handling as operational follow-up after upstream/live-environment validation

## Explicit Non-Goals

This spec does not cover:

- `XuanWu` agent-domain execution
- final `XuanWu -> xuanwu-gateway` invocation contract
- standalone wireless bridge service implementation

Those remain covered by the upstream and bridge-specific specs.
