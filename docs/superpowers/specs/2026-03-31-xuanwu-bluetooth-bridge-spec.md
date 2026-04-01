# xuanwu-bluetooth-bridge Spec

## Purpose

This document defines the standalone `xuanwu-bluetooth-bridge` service.

The bridge exists to keep Bluetooth hardware access, device discovery, pairing, connection lifecycle, and BLE/GATT protocol handling outside the main `xuanwu-iot-gateway` process while still exposing a stable API that `xuanwu-iot-gateway` can call.

## Goal

`xuanwu-bluetooth-bridge` must:

- run as an independent service on common operating systems
- manage local Bluetooth adapters and nearby Bluetooth devices
- expose a stable HTTP API to `xuanwu-iot-gateway`
- normalize Bluetooth device metadata, connection state, characteristic reads/writes, and notifications
- support production packaging as:
  - Linux RPM service
  - Windows Service

## Scope

### In scope

- Bluetooth adapter discovery and health
- BLE device discovery
- device pairing metadata management
- connect / disconnect lifecycle
- GATT characteristic read
- GATT characteristic write
- notification subscription
- event push back to `xuanwu-iot-gateway`
- OS service packaging and deployment guidance

### Out of scope

- direct `XuanWu` integration
- platform user/device truth
- global device registration truth
- non-Bluetooth wireless protocols

## Role Boundary

### `xuanwu-bluetooth-bridge`

Owns:

- host Bluetooth stack integration
- adapter enumeration
- scan session management
- device pairing/session lifecycle
- BLE/GATT protocol operations
- local hardware error handling

Does not own:

- user/device/channel truth
- agent truth
- gateway route truth
- long-term telemetry/event truth

### `xuanwu-iot-gateway`

Owns:

- northbound gateway API
- route selection
- capability mapping
- result normalization
- event and telemetry forwarding to `xuanwu-management-server`

`xuanwu-iot-gateway` treats `xuanwu-bluetooth-bridge` as a local or remote execution dependency.

## Deployment Modes

### Mode 1: remote bridge, recommended

`xuanwu-bluetooth-bridge` runs on the host or edge node that has Bluetooth hardware access.

`xuanwu-iot-gateway` calls the bridge over HTTP.

This is the default production model.

### Mode 2: same-host sidecar

`xuanwu-bluetooth-bridge` runs on the same machine as `xuanwu-iot-gateway` but still as a separate process or service.

This is acceptable for small installations and local development.

### Mode 3: embedded, deferred

An embedded bridge mode inside `xuanwu-iot-gateway` is explicitly deferred.

This spec assumes standalone service boundaries only.

## Supported Operating Systems

### Linux

Primary target:

- Ubuntu
- Debian
- CentOS Stream / RHEL compatible distributions
- edge Linux appliance distributions with BlueZ support

Requirements:

- BlueZ installed
- D-Bus available
- host Bluetooth adapter available

Packaging:

- RPM package for RPM-based distributions
- systemd unit file

### Windows

Primary target:

- Windows 10
- Windows 11
- Windows Server where Bluetooth stack access is available

Requirements:

- Windows Bluetooth stack available
- service account with access to Bluetooth APIs

Packaging:

- Windows Service
- MSI/zip or service-installer packaging

## Runtime Model

The bridge is stateful at runtime but not the source of truth.

It may maintain in-memory caches for:

- adapter status
- active scan sessions
- discovered device metadata
- active device connections
- notification subscriptions

It must not become the platform truth store for:

- business device ownership
- long-term telemetry history
- platform mappings

## Service Identity and Config

Minimum config:

```yaml
bridge_id: bluetooth-bridge-shanghai-01
listen_host: 0.0.0.0
listen_port: 9521
auth_token: change-me
scan:
  default_timeout_seconds: 10
  max_concurrent_scans: 2
connections:
  idle_disconnect_seconds: 120
  max_active_devices: 50
gateway:
  callback_base_url: http://xuanwu-iot-gateway:9510
  callback_token: change-me
platform:
  site_id: site-shanghai-01
  region_id: cn-east
```

## Northbound API

All endpoints are intended for `xuanwu-iot-gateway`.

Base prefix:

- `/bluetooth/v1`

### Health

- `GET /bluetooth/v1/health`

Returns:

- bridge status
- adapter availability
- active connection counts
- active scan count

### Adapter list

- `GET /bluetooth/v1/adapters`

Returns:

- local adapter list
- address
- powered state
- discoverable state

### Scan

- `POST /bluetooth/v1/scans:start`
- `POST /bluetooth/v1/scans/{scan_id}:stop`
- `GET /bluetooth/v1/scans/{scan_id}`

Request example:

```json
{
  "timeout_seconds": 8,
  "filters": {
    "name_prefix": "XW-",
    "service_uuids": ["180f", "181a"]
  }
}
```

### Devices

- `GET /bluetooth/v1/devices`
- `GET /bluetooth/v1/devices/{device_key}`

`device_key` is the bridge-local address key, for example a BLE MAC or OS-specific normalized identifier.

### Connections

- `POST /bluetooth/v1/devices/{device_key}:connect`
- `POST /bluetooth/v1/devices/{device_key}:disconnect`

### Characteristics

- `POST /bluetooth/v1/devices/{device_key}/characteristics:read`
- `POST /bluetooth/v1/devices/{device_key}/characteristics:write`
- `POST /bluetooth/v1/devices/{device_key}/characteristics:subscribe`
- `POST /bluetooth/v1/devices/{device_key}/characteristics:unsubscribe`

Read request example:

```json
{
  "service_uuid": "180f",
  "characteristic_uuid": "2a19",
  "encoding": "uint8"
}
```

Write request example:

```json
{
  "service_uuid": "12345678-1234-5678-1234-56789abcdef0",
  "characteristic_uuid": "12345678-1234-5678-1234-56789abcdef1",
  "encoding": "hex",
  "value": "01ff0a"
}
```

## Callback Contract To xuanwu-iot-gateway

The bridge must support asynchronous callback to `xuanwu-iot-gateway` for notifications and device events.

Suggested callback endpoints in `xuanwu-iot-gateway`:

- `POST /gateway/v1/ingest/http-push`
- `POST /gateway/v1/bridge/events`

Notification payload example:

```json
{
  "bridge_type": "bluetooth",
  "bridge_id": "bluetooth-bridge-shanghai-01",
  "device_key": "AA:BB:CC:DD:EE:FF",
  "event_type": "bluetooth.notification",
  "timestamp": "2026-03-31T10:30:00Z",
  "payload": {
    "service_uuid": "180f",
    "characteristic_uuid": "2a19",
    "encoding": "uint8",
    "value": 91
  }
}
```

## Capability Mapping Expectations

`xuanwu-bluetooth-bridge` does not understand platform capability codes.

Instead:

- `xuanwu-iot-gateway` maps `capability_code` to a bridge route
- the bridge only executes the requested Bluetooth operation

Example route payload from `xuanwu-iot-gateway` to the bridge:

```json
{
  "device_key": "AA:BB:CC:DD:EE:FF",
  "service_uuid": "180f",
  "characteristic_uuid": "2a19",
  "action": "read",
  "encoding": "uint8"
}
```

## Error Model

Required normalized errors:

- `adapter_unavailable`
- `scan_limit_reached`
- `device_not_found`
- `device_not_connectable`
- `device_not_connected`
- `pairing_required`
- `characteristic_not_found`
- `operation_timeout`
- `permission_denied`
- `host_stack_error`

Response shape:

```json
{
  "ok": false,
  "error": {
    "code": "device_not_connected",
    "message": "The target BLE device is not connected.",
    "details": {
      "device_key": "AA:BB:CC:DD:EE:FF"
    }
  }
}
```

## Security

Minimum requirements:

- shared bearer token or service token between gateway and bridge
- loopback or internal-network-only binding by default
- structured audit logs for connect/disconnect/read/write/subscribe operations

## Linux RPM Service Requirements

The Linux target must support RPM-oriented deployment.

Required deliverables:

- RPM build spec or equivalent packaging script
- installed binary or launcher at a stable path
- config directory, for example:
  - `/etc/xuanwu/bluetooth-bridge/config.yaml`
- data/log directory, for example:
  - `/var/lib/xuanwu/bluetooth-bridge`
  - `/var/log/xuanwu/bluetooth-bridge`
- systemd unit, for example:
  - `xuanwu-bluetooth-bridge.service`

Minimum systemd service expectations:

- automatic restart on failure
- configurable environment file
- dedicated service user when practical
- boot-time start enabled

## Windows Service Requirements

The Windows target must support standalone service deployment.

Required deliverables:

- service executable or Python service host wrapper
- config file path, for example:
  - `C:\\ProgramData\\XuanWu\\BluetoothBridge\\config.yaml`
- log directory, for example:
  - `C:\\ProgramData\\XuanWu\\BluetoothBridge\\logs`
- service name:
  - `XuanWuBluetoothBridge`

Minimum Windows service expectations:

- service start on boot
- graceful stop handling
- structured file logging
- configuration reload on restart

## Observability

Required outputs:

- structured logs
- bridge_id
- device_key
- request_id
- trace_id when supplied by gateway
- counters for:
  - scans started
  - devices discovered
  - connections opened
  - characteristic reads
  - characteristic writes
  - notification events
  - failures by error code

## Test and Acceptance Criteria

Completion requires:

- Linux service packaging spec present
- Windows service packaging spec present
- health, scan, connect, read, write, subscribe APIs defined
- callback contract to `xuanwu-iot-gateway` defined
- normalized error model defined
- realistic integration test plan defined

Minimum realistic test scenarios:

- scan returns valid discovered device metadata
- connect to a valid BLE device
- read battery characteristic
- write to a writable characteristic
- subscribe to notifications and receive at least one event
- bridge restart does not corrupt runtime metadata

