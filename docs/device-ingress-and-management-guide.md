# Device Ingress and Management Guide

## Purpose

This guide explains how devices enter the system, how they become managed devices, and how data closes the loop between ingress services and management.

## Three Service Roles

### `xuanwu-management-server`

This is the source of truth for:

- managed devices
- discovered devices
- ownership and lifecycle
- mappings
- telemetry, events, alarms, and schedules

### `xuanwu-device-gateway`

This is the ingress for conversational and runtime session devices.

It is responsible for:

- runtime connection handling
- OTA and session entrypoints
- first-contact discovery callback
- runtime heartbeat callback

### `xuanwu-iot-gateway`

This is the ingress for IoT, industrial, sensor, and actuator devices.

It is responsible for:

- protocol access
- command execution
- ingest normalization
- device discovery callback
- device heartbeat callback

## Two Device Layers

### Discovered Device

A discovered device is not yet the formal managed record.

It exists so that:

- a gateway can report a newly observed device
- the device gateway can report first contact from a runtime device
- a user can later review and promote or ignore it

### Managed Device

A managed device is the formal record used for:

- ownership
- lifecycle
- channel mapping
- agent mapping
- portal operations
- unified detail views

## Ingress Flow From `xuanwu-iot-gateway`

1. A gateway adapter sees a new device.
2. The IoT gateway normalizes:
   - `device_id`
   - `gateway_id`
   - `protocol_type`
   - `adapter_type`
   - `device_kind`
3. The IoT gateway calls management discovery ingress.
4. Management creates or updates a discovered-device record.
5. Portal shows the item in the discovered-device list.
6. An operator promotes or ignores it.
7. Promotion creates the formal managed-device record.

## Ingress Flow From `xuanwu-device-gateway`

1. A conversational device makes first contact.
2. The device gateway determines that the device is not yet known.
3. The device gateway calls management discovery ingress with `ingress_type=device_server`.
4. Management creates or updates the discovered-device record.
5. The operator promotes or ignores it.
6. Once managed, runtime config resolve works against the managed-device record.

## Data Loop After A Device Is Managed

After management owns the formal device record:

- `xuanwu-iot-gateway` continues to send:
  - telemetry
  - events
  - command results
  - heartbeat
- `xuanwu-device-gateway` continues to send:
  - runtime heartbeat
  - runtime-side activity updates

Management updates unified recency fields such as:

- `last_seen_at`
- `last_event_at`
- `last_telemetry_at`
- `last_command_at`

Portal then reads only from management-owned state.

## Current Closed Loops

The following loops are already closed locally:

- gateway discovery -> management discovered device -> portal review
- device-gateway first contact -> management discovered device -> portal review
- discovered device -> promote or ignore
- telemetry and event ingress -> management persistence -> portal read models
- command result ingress -> management persistence -> portal read models
- heartbeat ingress -> management recency update -> portal device detail

## What Is Still Not Fully Closed

The remaining major open loop is upstream:

- `XuanWu` still needs to drive final agent-based device execution against `xuanwu-iot-gateway`

Repository-local code is already prepared for the management, ingress, and data loop side of that flow.
