# xuanwu-nearlink-bridge Spec

## Purpose

This document defines the standalone `xuanwu-nearlink-bridge` service.

The bridge exists to isolate NearLink or star-flash class hardware integration, vendor SDKs, dongles, and low-latency local wireless operations from the main `xuanwu-gateway` process.

## Goal

`xuanwu-nearlink-bridge` must:

- run as an independent service on common operating systems
- manage local NearLink-capable hardware or vendor bridge SDKs
- expose a stable HTTP API to `xuanwu-gateway`
- normalize device discovery, addressing, command execution, state query, and event callbacks
- support production packaging as:
  - Linux RPM service
  - Windows Service

## Scope

### In scope

- local NearLink bridge runtime
- local dongle or adapter health
- device discovery metadata
- device addressing and session lifecycle
- command dispatch
- state query
- event and telemetry callback to `xuanwu-gateway`
- OS service packaging and deployment guidance

### Out of scope

- vendor-independent RF stack implementation inside `xuanwu-gateway`
- platform source-of-truth device ownership
- `XuanWu` domain logic

## Role Boundary

### `xuanwu-nearlink-bridge`

Owns:

- local NearLink hardware or SDK integration
- bridge-local discovery and connectivity
- command translation to the vendor/runtime protocol
- bridge-local device state collection
- local transport errors and retry behavior

Does not own:

- business mappings
- platform capability mappings
- user/channel/device truth
- agent decision logic

### `xuanwu-gateway`

Owns:

- northbound gateway contract
- capability routing
- normalized command result model
- event and telemetry forwarding

## Deployment Modes

### Remote bridge, recommended

`xuanwu-nearlink-bridge` runs where the NearLink radio hardware or vendor SDK can run safely.

This is the expected production model.

### Same-host sidecar

Allowed for smaller deployments where `xuanwu-gateway` and the NearLink bridge share the same host.

### Embedded mode, deferred

Embedding the NearLink bridge inside `xuanwu-gateway` is explicitly deferred.

## Supported Operating Systems

### Linux

Primary target:

- Ubuntu
- Debian
- CentOS Stream / RHEL compatible distributions
- industrial Linux edge appliances

Requirements depend on the chosen vendor implementation:

- vendor SDK or bridge library installed
- device node or USB access when dongles are used
- service account with hardware access

Packaging:

- RPM package for RPM-based distributions
- systemd unit file

### Windows

Primary target:

- Windows 10
- Windows 11
- Windows Server where vendor SDK support exists

Requirements:

- vendor runtime installed when required
- service account with device access

Packaging:

- Windows Service
- MSI/zip or service-installer packaging

## Runtime Model

The bridge is stateful but not authoritative.

It may cache:

- discovered device metadata
- active sessions
- local adapter state
- vendor-runtime handles

It must not become long-term platform truth.

## Service Identity and Config

Minimum config:

```yaml
bridge_id: nearlink-bridge-shanghai-01
listen_host: 0.0.0.0
listen_port: 9531
auth_token: change-me
vendor:
  driver_type: generic_http_sdk
  endpoint: http://127.0.0.1:19031
  api_key: change-me
discovery:
  default_timeout_seconds: 5
sessions:
  idle_disconnect_seconds: 60
  max_active_devices: 100
gateway:
  callback_base_url: http://xuanwu-gateway:9510
  callback_token: change-me
platform:
  site_id: site-shanghai-01
  region_id: cn-east
```

## Northbound API

Base prefix:

- `/nearlink/v1`

### Health

- `GET /nearlink/v1/health`

Returns:

- bridge status
- radio or SDK availability
- active session counts

### Adapters

- `GET /nearlink/v1/adapters`

Returns:

- local NearLink adapter or runtime availability
- firmware/runtime version when available

### Discovery

- `POST /nearlink/v1/discovery:start`
- `POST /nearlink/v1/discovery/{discovery_id}:stop`
- `GET /nearlink/v1/discovery/{discovery_id}`

Request example:

```json
{
  "timeout_seconds": 5,
  "filters": {
    "product_codes": ["nl-sensor", "nl-actuator"],
    "name_prefix": "XW-"
  }
}
```

### Devices

- `GET /nearlink/v1/devices`
- `GET /nearlink/v1/devices/{device_key}`

### Sessions

- `POST /nearlink/v1/devices/{device_key}:connect`
- `POST /nearlink/v1/devices/{device_key}:disconnect`

### Commands

- `POST /nearlink/v1/devices/{device_key}:command`

Request example:

```json
{
  "command_type": "capability.invoke",
  "capability_code": "switch.on_off",
  "action": "turn_on",
  "arguments": {}
}
```

### State Query

- `POST /nearlink/v1/devices/{device_key}:query-state`

## Callback Contract To xuanwu-gateway

The bridge must support callback to `xuanwu-gateway` for:

- command result notifications
- device online/offline state changes
- telemetry
- asynchronous events

Suggested callback endpoints in `xuanwu-gateway`:

- `POST /gateway/v1/ingest/http-push`
- `POST /gateway/v1/bridge/events`
- `POST /gateway/v1/commands:dispatch-result`

Asynchronous event example:

```json
{
  "bridge_type": "nearlink",
  "bridge_id": "nearlink-bridge-shanghai-01",
  "device_key": "NL-001-45A9",
  "event_type": "nearlink.state.changed",
  "timestamp": "2026-03-31T11:05:00Z",
  "payload": {
    "online": true,
    "signal_strength": -58,
    "battery": 87
  }
}
```

## Capability Mapping Expectations

`xuanwu-nearlink-bridge` does not own platform capability routing.

`xuanwu-gateway` maps platform routes into bridge-native calls and sends normalized command/query payloads.

The bridge must execute the request and return a bridge-local normalized result.

## Error Model

Required normalized errors:

- `adapter_unavailable`
- `vendor_runtime_unavailable`
- `discovery_limit_reached`
- `device_not_found`
- `device_not_connected`
- `device_busy`
- `command_not_supported`
- `query_not_supported`
- `operation_timeout`
- `permission_denied`
- `host_stack_error`

Response shape:

```json
{
  "ok": false,
  "error": {
    "code": "vendor_runtime_unavailable",
    "message": "The NearLink vendor runtime is not available.",
    "details": {
      "bridge_id": "nearlink-bridge-shanghai-01"
    }
  }
}
```

## Security

Minimum requirements:

- shared service token between gateway and bridge
- optional vendor API key passthrough when required
- internal-network-only binding by default
- structured audit logs for discovery, connect, command, query, and disconnect

## Linux RPM Service Requirements

Required deliverables:

- RPM build spec or equivalent packaging script
- installed launcher path
- config directory, for example:
  - `/etc/xuanwu/nearlink-bridge/config.yaml`
- data/log directories, for example:
  - `/var/lib/xuanwu/nearlink-bridge`
  - `/var/log/xuanwu/nearlink-bridge`
- systemd unit:
  - `xuanwu-nearlink-bridge.service`

Minimum service expectations:

- automatic restart on failure
- environment file support
- dedicated service user when practical
- vendor runtime dependency checks on start

## Windows Service Requirements

Required deliverables:

- service executable or Python service wrapper
- config path, for example:
  - `C:\\ProgramData\\XuanWu\\NearLinkBridge\\config.yaml`
- log directory, for example:
  - `C:\\ProgramData\\XuanWu\\NearLinkBridge\\logs`
- Windows service name:
  - `XuanWuNearLinkBridge`

Minimum service expectations:

- starts at boot
- graceful stop handling
- startup validation of vendor runtime presence
- structured file logging

## Observability

Required outputs:

- structured logs
- bridge_id
- device_key
- request_id
- trace_id when supplied
- counters for:
  - discovery sessions
  - devices discovered
  - sessions opened
  - commands executed
  - state queries
  - callbacks sent
  - failures by error code

## Test and Acceptance Criteria

Completion requires:

- Linux RPM service packaging spec present
- Windows service packaging spec present
- discovery, connect, command, query, disconnect APIs defined
- callback contract to `xuanwu-gateway` defined
- normalized error model defined
- realistic integration test plan defined

Minimum realistic test scenarios:

- discovery returns valid device metadata
- connect to a valid bridge-managed device
- execute a command against a discovered device
- query device state successfully
- emit one async state event back to gateway
- recover cleanly after bridge process restart

