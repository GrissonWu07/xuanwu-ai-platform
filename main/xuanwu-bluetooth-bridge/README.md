# xuanwu-bluetooth-bridge

`xuanwu-bluetooth-bridge` is the standalone Bluetooth bridge service for the local XuanWu platform stack.

It isolates host Bluetooth integration from `xuanwu-iot-gateway` while exposing a stable HTTP API for:

- adapter health
- device discovery
- connect/disconnect lifecycle
- GATT characteristic read/write
- notification subscription
- callback into `xuanwu-iot-gateway`

## Implemented APIs

- `GET /bluetooth/v1/health`
- `GET /bluetooth/v1/adapters`
- `POST /bluetooth/v1/scans:start`
- `POST /bluetooth/v1/scans/{scan_id}:stop`
- `GET /bluetooth/v1/scans/{scan_id}`
- `GET /bluetooth/v1/devices`
- `GET /bluetooth/v1/devices/{device_key}`
- `POST /bluetooth/v1/devices/{device_key}:connect`
- `POST /bluetooth/v1/devices/{device_key}:disconnect`
- `POST /bluetooth/v1/devices/{device_key}/characteristics:read`
- `POST /bluetooth/v1/devices/{device_key}/characteristics:write`
- `POST /bluetooth/v1/devices/{device_key}/characteristics:subscribe`
- `POST /bluetooth/v1/devices/{device_key}/characteristics:unsubscribe`
