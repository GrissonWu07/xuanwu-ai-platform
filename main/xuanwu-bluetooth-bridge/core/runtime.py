from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone


class BluetoothBridgeError(Exception):
    def __init__(self, code: str, message: str, *, status: int = 400, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.details = details or {}


class BluetoothBridgeRuntime:
    def __init__(self, config: dict, *, callback_client=None):
        bridge_config = config.get("bridge", {})
        self.bridge_config = bridge_config
        self.callback_client = callback_client
        self.bridge_id = str(bridge_config.get("bridge_id") or "bluetooth-bridge-local")
        self.adapters = [
            {
                "adapter_id": "bluetooth-default",
                "address": "AA:BB:CC:DD:EE:00",
                "powered": True,
                "discoverable": True,
            }
        ]
        self.scans: dict[str, dict] = {}
        self.devices: dict[str, dict] = {}
        self.connections: dict[str, dict] = {}
        self.subscriptions: dict[str, dict] = {}
        self._scan_counter = 0
        self._seed_demo_devices()

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _seed_demo_devices(self) -> None:
        if not self.bridge_config.get("demo", {}).get("enabled", True):
            return
        prefix = str(self.bridge_config.get("demo", {}).get("device_prefix") or "XW-BLE")
        for suffix, service_uuid in (("01", "180f"), ("02", "181a")):
            device_key = f"AA:BB:CC:DD:EE:{suffix}"
            self.devices.setdefault(
                device_key,
                {
                    "device_key": device_key,
                    "display_name": f"{prefix}-{suffix}",
                    "device_kind": "sensor" if suffix == "02" else "actuator",
                    "address": device_key,
                    "service_uuids": [service_uuid],
                    "signal_strength": -52 if suffix == "01" else -60,
                    "first_seen_at": self._timestamp(),
                    "last_seen_at": self._timestamp(),
                    "connection_state": "discovered",
                    "characteristics": {
                        f"{service_uuid}:2a19": {"encoding": "uint8", "value": 87 if suffix == "01" else 68},
                    },
                },
            )

    def _require_device(self, device_key: str) -> dict:
        device = self.devices.get(device_key)
        if device is None:
            raise BluetoothBridgeError(
                "device_not_found",
                "The target BLE device was not found.",
                status=404,
                details={"device_key": device_key},
            )
        return device

    def _require_connected(self, device_key: str) -> dict:
        connection = self.connections.get(device_key)
        if connection is None or connection.get("status") != "connected":
            raise BluetoothBridgeError(
                "device_not_connected",
                "The target BLE device is not connected.",
                status=409,
                details={"device_key": device_key},
            )
        return connection

    def _build_scan_result(self, payload: dict) -> list[dict]:
        filters = dict(payload.get("filters") or {})
        name_prefix = str(filters.get("name_prefix") or "").strip()
        service_uuids = {str(item).lower() for item in filters.get("service_uuids") or [] if str(item).strip()}
        discovered = []
        for device in self.devices.values():
            if name_prefix and not str(device.get("display_name") or "").startswith(name_prefix):
                continue
            if service_uuids:
                current = {str(item).lower() for item in device.get("service_uuids") or []}
                if current.isdisjoint(service_uuids):
                    continue
            record = deepcopy(device)
            record["discovered_at"] = self._timestamp()
            discovered.append(record)
        return discovered

    def list_adapters(self) -> list[dict]:
        return deepcopy(self.adapters)

    def list_devices(self) -> list[dict]:
        return [deepcopy(item) for item in self.devices.values()]

    def get_device(self, device_key: str) -> dict:
        device = self._require_device(device_key)
        device["last_seen_at"] = self._timestamp()
        return deepcopy(device)

    async def start_scan(self, payload: dict) -> dict:
        max_scans = int(self.bridge_config.get("scan", {}).get("max_concurrent_scans", 2))
        active_count = len([item for item in self.scans.values() if item.get("status") == "running"])
        if active_count >= max_scans:
            raise BluetoothBridgeError("scan_limit_reached", "The scan limit has been reached.", status=409)
        self._scan_counter += 1
        scan_id = f"scan-{self._scan_counter:04d}"
        timeout = int(payload.get("timeout_seconds") or self.bridge_config.get("scan", {}).get("default_timeout_seconds", 8))
        record = {
            "scan_id": scan_id,
            "status": "completed",
            "timeout_seconds": timeout,
            "started_at": self._timestamp(),
            "finished_at": self._timestamp(),
            "filters": deepcopy(payload.get("filters") or {}),
            "devices": self._build_scan_result(payload),
        }
        self.scans[scan_id] = record
        return deepcopy(record)

    def stop_scan(self, scan_id: str) -> dict:
        scan = self.scans.get(scan_id)
        if scan is None:
            raise BluetoothBridgeError("scan_not_found", "The scan session was not found.", status=404)
        scan["status"] = "stopped"
        scan["finished_at"] = self._timestamp()
        return deepcopy(scan)

    def get_scan(self, scan_id: str) -> dict:
        scan = self.scans.get(scan_id)
        if scan is None:
            raise BluetoothBridgeError("scan_not_found", "The scan session was not found.", status=404)
        return deepcopy(scan)

    async def connect_device(self, device_key: str) -> dict:
        device = self._require_device(device_key)
        max_devices = int(self.bridge_config.get("connections", {}).get("max_active_devices", 50))
        if len(self.connections) >= max_devices and device_key not in self.connections:
            raise BluetoothBridgeError("connection_limit_reached", "The active connection limit has been reached.", status=409)
        connection = {
            "device_key": device_key,
            "status": "connected",
            "connected_at": self._timestamp(),
            "last_activity_at": self._timestamp(),
        }
        self.connections[device_key] = connection
        device["connection_state"] = "connected"
        if self.callback_client is not None:
            await self.callback_client.post_bridge_event(
                {
                    "bridge_type": "bluetooth",
                    "bridge_id": self.bridge_id,
                    "device_key": device_key,
                    "event_type": "bluetooth.device.connected",
                    "timestamp": self._timestamp(),
                    "payload": {"online": True},
                }
            )
        return deepcopy(connection)

    async def disconnect_device(self, device_key: str) -> dict:
        self._require_device(device_key)
        self.connections.pop(device_key, None)
        for key in [key for key, item in self.subscriptions.items() if item.get("device_key") == device_key]:
            self.subscriptions.pop(key, None)
        self.devices[device_key]["connection_state"] = "discovered"
        payload = {
            "device_key": device_key,
            "status": "disconnected",
            "disconnected_at": self._timestamp(),
        }
        if self.callback_client is not None:
            await self.callback_client.post_bridge_event(
                {
                    "bridge_type": "bluetooth",
                    "bridge_id": self.bridge_id,
                    "device_key": device_key,
                    "event_type": "bluetooth.device.disconnected",
                    "timestamp": self._timestamp(),
                    "payload": {"online": False},
                }
            )
        return payload

    def read_characteristic(self, device_key: str, payload: dict) -> dict:
        self._require_connected(device_key)
        key = f"{payload['service_uuid']}:{payload['characteristic_uuid']}"
        value = self.devices[device_key]["characteristics"].get(
            key,
            {"encoding": payload.get("encoding") or "hex", "value": 0},
        )
        return {
            "device_key": device_key,
            "service_uuid": payload["service_uuid"],
            "characteristic_uuid": payload["characteristic_uuid"],
            "encoding": value.get("encoding"),
            "value": value.get("value"),
            "read_at": self._timestamp(),
        }

    async def write_characteristic(self, device_key: str, payload: dict) -> dict:
        self._require_connected(device_key)
        key = f"{payload['service_uuid']}:{payload['characteristic_uuid']}"
        self.devices[device_key]["characteristics"][key] = {
            "encoding": payload.get("encoding") or "hex",
            "value": payload.get("value"),
        }
        result = {
            "device_key": device_key,
            "service_uuid": payload["service_uuid"],
            "characteristic_uuid": payload["characteristic_uuid"],
            "encoding": payload.get("encoding") or "hex",
            "value": payload.get("value"),
            "written_at": self._timestamp(),
        }
        if self.callback_client is not None:
            await self.callback_client.post_command_result(
                {
                    "request_id": payload.get("request_id"),
                    "gateway_id": payload.get("gateway_id"),
                    "adapter_type": "bluetooth",
                    "status": "succeeded",
                    "result": {
                        "device_id": payload.get("device_id"),
                        "command_name": "write_characteristic",
                        "protocol_response": result,
                    },
                }
            )
        return result

    async def subscribe_characteristic(self, device_key: str, payload: dict) -> dict:
        self._require_connected(device_key)
        key = f"{payload['service_uuid']}:{payload['characteristic_uuid']}"
        subscription = {
            "device_key": device_key,
            "service_uuid": payload["service_uuid"],
            "characteristic_uuid": payload["characteristic_uuid"],
            "encoding": payload.get("encoding") or "hex",
            "subscribed_at": self._timestamp(),
        }
        self.subscriptions[key] = subscription
        current_value = self.devices[device_key]["characteristics"].get(
            key,
            {"encoding": payload.get("encoding") or "hex", "value": payload.get("value", 0)},
        )
        if self.callback_client is not None:
            await self.callback_client.post_http_push(
                {
                    "adapter_type": "sensor_http_push",
                    "device_id": payload.get("device_id") or device_key,
                    "gateway_id": payload.get("gateway_id") or self.bridge_id,
                    "discovery_id": f"bluetooth:{self.bridge_id}:{device_key}",
                    "display_name": self.devices[device_key].get("display_name"),
                    "device_kind": self.devices[device_key].get("device_kind", "sensor"),
                    "protocol_type": "bluetooth",
                    "observed_at": self._timestamp(),
                    "telemetry": {key: current_value.get("value")},
                }
            )
        return deepcopy(subscription)

    def unsubscribe_characteristic(self, device_key: str, payload: dict) -> dict:
        self._require_connected(device_key)
        key = f"{payload['service_uuid']}:{payload['characteristic_uuid']}"
        self.subscriptions.pop(key, None)
        return {
            "device_key": device_key,
            "service_uuid": payload["service_uuid"],
            "characteristic_uuid": payload["characteristic_uuid"],
            "status": "unsubscribed",
            "unsubscribed_at": self._timestamp(),
        }
