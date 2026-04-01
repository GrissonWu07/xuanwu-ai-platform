# xuanwu-nearlink-bridge

`xuanwu-nearlink-bridge` is the standalone NearLink bridge service for the local XuanWu platform stack.

It isolates NearLink radio integration, vendor runtime access, and device session handling from `xuanwu-iot-gateway`.

## Implemented APIs

- `GET /nearlink/v1/health`
- `GET /nearlink/v1/adapters`
- `POST /nearlink/v1/discovery:start`
- `POST /nearlink/v1/discovery/{discovery_id}:stop`
- `GET /nearlink/v1/discovery/{discovery_id}`
- `GET /nearlink/v1/devices`
- `GET /nearlink/v1/devices/{device_key}`
- `POST /nearlink/v1/devices/{device_key}:connect`
- `POST /nearlink/v1/devices/{device_key}:disconnect`
- `POST /nearlink/v1/devices/{device_key}:command`
- `POST /nearlink/v1/devices/{device_key}:query-state`
