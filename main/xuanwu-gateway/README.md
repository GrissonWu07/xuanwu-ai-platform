# xuanwu-gateway

`xuanwu-gateway` is the protocol execution layer for IoT, industrial, and wireless devices in the local XuanWu platform stack.

## Implemented APIs

- `GET /gateway/v1/adapters`
- `GET /gateway/v1/health`
- `GET /gateway/v1/config`
- `POST /gateway/v1/commands`
- `POST /gateway/v1/commands:dispatch`
- `POST /gateway/v1/jobs:execute`
- `POST /gateway/v1/ingest/http-push`
- `POST /gateway/v1/ingest/mqtt`
- `GET /gateway/v1/devices/{device_id}/state`

## Implemented Adapter Families

- `http`
- `mqtt`
- `home_assistant`
- `sensor_http_push`
- `sensor_mqtt`
- `modbus_tcp`
- `opc_ua`
- `bacnet_ip`
- `can_gateway`
- `bluetooth`
- `nearlink`

## Boundaries

`xuanwu-gateway` owns:

- southbound protocol execution
- adapter validation
- command result normalization
- telemetry and event normalization

`xuanwu-management-server` owns:

- gateway definitions
- gateway routes
- capability catalog
- telemetry, event, and command-result persistence

`XuanWu` owns:

- Agent decisions
- capability selection
- device invocation intent

## Verification

Run the gateway suite with:

```bash
python -m pytest main/xuanwu-gateway/tests -q
```
