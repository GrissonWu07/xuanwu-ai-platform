# xuanwu-gateway Adapter Completion Spec

## Purpose

This document defines the missing implementation work required to move `xuanwu-gateway` from a registry-and-skeleton foundation into a usable IoT and industrial protocol execution layer.

This spec exists because the current repository state only provides:

- adapter registry
- command dispatch framework
- health/config/device-state surfaces
- adapter directory layout
- dry-run or skeleton adapter placeholders

That is not sufficient to satisfy the gateway-related platform specs.

## Goal

`xuanwu-gateway` must support real protocol-backed execution for the first production-ready adapter set, while preserving the existing unified command contract.

## Current State

### Present in code

- core registry
- base adapter abstraction
- HTTP adapter scaffold
- MQTT adapter scaffold
- Home Assistant adapter scaffold
- gateway handler and dispatch surface
- adapter directories for:
  - conversation/websocket
  - conversation/mqtt_gateway
  - actuator/http
  - actuator/mqtt
  - actuator/home_assistant
  - sensor/mqtt
  - sensor/http_push
  - industrial/modbus_tcp
  - industrial/opc_ua
  - industrial/bacnet_ip
  - industrial/can_gateway

### Missing

- protocol-backed adapter implementations
- protocol-specific configuration validation
- standardized capability-to-protocol action mapping
- adapter-level retries and timeout rules
- adapter-level error normalization
- realistic protocol integration tests

### Remaining gap after the first adapter pass

The repository now has real adapter entrypoints and test-covered baseline implementations, but the following areas are still below the intended completion bar:

- MQTT support is currently publish-oriented only and does not yet define broker-backed subscription ingestion or broker service deployment requirements
- Home Assistant support is currently service-call oriented and does not yet define entity state read, state sync, or event-stream expectations
- industrial adapters provide baseline read/write flows but do not yet define richer operation coverage and deployment dependencies in one place
- runtime packaging does not yet formalize required Python dependencies and gateway container build expectations
- wireless bridge services are not yet implemented as independent services, even though the gateway contract now expects bridge-style execution for Bluetooth and NearLink

## Required Completion Standard

An adapter family is considered complete only when all of the following are true:

- It accepts a real gateway route and device definition
- It executes a real protocol action or query
- It returns a normalized `CapabilityCommandResult`
- It can emit normalized telemetry/event payloads
- It has configuration validation
- It has failure-mode handling
- It has realistic tests with valid protocol-shaped payloads

Dry-run stubs and simple no-op returns do not count as completion.

## Adapter Priority

### Priority 1: must complete first

- `actuator/http`
- `actuator/mqtt`
- `actuator/home_assistant`
- `sensor/mqtt`
- `sensor/http_push`

These five cover the broadest early platform value.

### Priority 2: industrial baseline

- `industrial/modbus_tcp`

This is the first industrial adapter that should move past skeleton level.

### Priority 3: industrial expansion

- `industrial/opc_ua`
- `industrial/bacnet_ip`
- `industrial/can_gateway`

These can follow after Modbus TCP is stable.

### Priority 4: wireless device expansion

- `wireless/bluetooth`
- `wireless/nearlink`

These must be included as first-class gateway families for future wearable, proximity, low-power accessory, and star-flash class devices.

### Deferred

- conversation-class gateway adapters

Conversation devices remain primarily owned by `xuanwu-device-server`, so these gateway adapter directories can stay lower priority for now.

## Protocol Matrix

| Adapter family | Current status | Required target |
| --- | --- | --- |
| `actuator/http` | Skeleton | Real HTTP command adapter |
| `actuator/mqtt` | Skeleton | Real MQTT publish adapter |
| `actuator/home_assistant` | Skeleton | Real Home Assistant service-call adapter |
| `sensor/mqtt` | Skeleton | Real MQTT telemetry ingestion adapter |
| `sensor/http_push` | Skeleton | Real HTTP telemetry ingestion adapter |
| `industrial/modbus_tcp` | Directory only | Real Modbus TCP read/write adapter |
| `industrial/opc_ua` | Directory only | Real OPC UA browse/read/write adapter |
| `industrial/bacnet_ip` | Directory only | Real BACnet/IP property adapter |
| `industrial/can_gateway` | Directory only | Real CAN gateway command/state adapter |
| `wireless/bluetooth` | Not present yet | Real Bluetooth command/state adapter family |
| `wireless/nearlink` | Not present yet | Real NearLink command/state adapter family |

## Required Capabilities By Adapter Family

### `actuator/http`

Must support:

- mapped HTTP method execution
- header/body/query parameter mapping
- timeout handling
- success and error normalization
- optional state follow-up read

### `actuator/mqtt`

Must support:

- publish topic resolution
- payload templating from capability arguments
- QoS and retain configuration
- acknowledgement strategy
- command timeout and publish failure handling

### `actuator/home_assistant`

Must support:

- Home Assistant service invocation
- entity and service resolution
- auth token usage
- normalized success/failure mapping

### `sensor/mqtt`

Must support:

- topic subscription mapping
- payload decoding
- telemetry normalization
- event normalization
- management-server callback integration

### `sensor/http_push`

Must support:

- inbound HTTP event normalization
- route-level validation
- telemetry schema mapping
- signature/auth validation when configured

### `industrial/modbus_tcp`

Must support:

- coil read/write
- discrete input read
- holding register read/write
- input register read
- address and unit-id mapping
- typed value decoding/encoding

### `industrial/opc_ua`

Must support:

- node browse/read/write for configured nodes
- typed value mapping
- session lifecycle handling

### `industrial/bacnet_ip`

Must support:

- property read/write for configured object/property routes
- object addressing and normalization

### `industrial/can_gateway`

Must support:

- command frame emission through the selected CAN bridge
- decoded state reads for configured signals
- route-level signal mapping

### `wireless/bluetooth`

Must support:

- gateway-mediated BLE device discovery metadata
- characteristic read/write mapping
- notification/event normalization
- route-level pairing and addressing metadata

### `wireless/nearlink`

Must support:

- gateway-mediated NearLink device addressing
- low-latency command dispatch mapping
- state/event normalization
- route-level transport and topology metadata

## Implementation Boundaries

`xuanwu-gateway` owns:

- protocol execution
- adapter configuration validation
- adapter error normalization
- telemetry/event normalization

`xuanwu-management-server` owns:

- gateway definitions
- gateway routes
- device metadata
- capability catalog
- event and telemetry persistence

`XuanWu` owns:

- decision to invoke a capability
- selection of target capability and arguments

## API Contract Requirements

The current gateway HTTP surfaces remain the northbound contract:

- `POST /gateway/v1/commands`
- `POST /gateway/v1/commands:dispatch`
- `GET /gateway/v1/devices/{device_id}/state`
- `POST /gateway/v1/jobs:execute`

Each completed adapter family must work through these unified surfaces.

No adapter-specific public API should bypass the standard gateway contract.

## Configuration Requirements

Each adapter family must define:

- required route fields
- optional route fields
- auth fields
- timeout defaults
- retry defaults
- supported capability codes

This validation must occur before protocol execution begins.

The gateway implementation must also define a concrete dependency and packaging model for:

- `pymodbus`
- `opcua` or `asyncua`
- `BAC0`
- `paho-mqtt`

It must also document that an MQTT broker is external infrastructure and not an in-process replacement inside `xuanwu-gateway`.

## Remaining Adapter-Specific Completion Work

### MQTT

Still required beyond the current baseline:

- broker-oriented subscription ingestion contract
- stable topic-to-telemetry mapping profile
- explicit broker deployment expectation
- clearer retained-message and QoS handling guidance
- runtime dependency packaging for `paho-mqtt`

Gateway acceptance for MQTT should include both:

- command publish
- inbound telemetry/event ingestion through a broker-backed flow

### Home Assistant

Still required beyond the current baseline:

- entity-state read capability
- normalized `device state` pull contract
- optional event-stream sync strategy definition
- clearer route schema for entity metadata and domain/service separation

Gateway acceptance for Home Assistant should include:

- service invocation
- entity state read

### Modbus TCP

Still required beyond the current baseline:

- discrete input read
- input register read
- coil read
- clearer function-to-command mapping table
- dependency packaging for `pymodbus`

### OPC UA

Still required beyond the current baseline:

- browse/read/write operation contract
- explicit dependency packaging for the chosen OPC UA library
- clearer security/session expectations

### BACnet/IP

Still required beyond the current baseline:

- explicit `BAC0` deployment requirements
- clearer network-mode expectations for Docker and host networking
- object/property route examples beyond a single property read/write pair

### CAN gateway

Still required beyond the current baseline:

- stronger external bridge contract examples
- state-query examples, not only command examples

### Wireless adapters

Still required beyond the current baseline:

- standalone bridge specs for Bluetooth and NearLink
- external bridge deployment guidance
- bridge callback validation against the gateway ingest contract

## Testing Requirements

Tests must use valid protocol-shaped data and must not be placeholder-only tests.

Required test types:

- route validation tests
- command normalization tests
- result normalization tests
- protocol error normalization tests
- end-to-end handler tests through gateway HTTP surfaces

Where a real external dependency is too heavy for the local suite, use:

- realistic protocol-shaped fixtures
- deterministic fake transports
- strict assertion on normalized contract output

## Completion Order

1. `actuator/http`
2. `sensor/http_push`
3. `actuator/home_assistant`
4. `actuator/mqtt`
5. `sensor/mqtt`
6. `industrial/modbus_tcp`
7. `industrial/opc_ua`
8. `industrial/bacnet_ip`
9. `industrial/can_gateway`
10. `wireless/bluetooth`
11. `wireless/nearlink`

## Definition of Done

The gateway adapter implementation spec is complete only when:

- the Priority 1 adapter families are fully real implementations
- `industrial/modbus_tcp` is implemented as the first industrial baseline
- realistic tests exist for each completed family
- `xuanwu-gateway` is no longer accurately described as "skeleton adapters"

