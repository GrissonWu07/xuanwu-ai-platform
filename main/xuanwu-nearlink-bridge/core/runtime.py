from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone


class NearlinkBridgeError(Exception):
    def __init__(self, code: str, message: str, *, status: int = 400, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.details = details or {}


class NearlinkBridgeRuntime:
    def __init__(self, config: dict, *, callback_client=None):
        bridge_config = config.get("bridge", {})
        self.bridge_config = bridge_config
        self.callback_client = callback_client
        self.bridge_id = str(bridge_config.get("bridge_id") or "nearlink-bridge-local")
        self.adapters = [{"adapter_id": "nearlink-default", "runtime": "demo", "available": True}]
        self.discovery_sessions: dict[str, dict] = {}
        self.devices: dict[str, dict] = {}
        self.sessions: dict[str, dict] = {}
        self._discovery_counter = 0
        self._seed_demo_devices()

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _seed_demo_devices(self) -> None:
        if not self.bridge_config.get("demo", {}).get("enabled", True):
            return
        prefix = str(self.bridge_config.get("demo", {}).get("device_prefix") or "XW-NL")
        for suffix, kind in (("001", "actuator"), ("002", "sensor")):
            device_key = f"NL-{suffix}"
            self.devices.setdefault(
                device_key,
                {
                    "device_key": device_key,
                    "display_name": f"{prefix}-{suffix}",
                    "device_kind": kind,
                    "product_code": f"nl-{kind}",
                    "signal_strength": -58 if kind == "actuator" else -63,
                    "state": {"online": False, "battery": 82 if kind == "sensor" else 100},
                    "first_seen_at": self._timestamp(),
                    "last_seen_at": self._timestamp(),
                },
            )

    def _require_device(self, device_key: str) -> dict:
        device = self.devices.get(device_key)
        if device is None:
            raise NearlinkBridgeError("device_not_found", "The NearLink device was not found.", status=404)
        return device

    def _require_session(self, device_key: str) -> dict:
        session = self.sessions.get(device_key)
        if session is None or session.get("status") != "connected":
            raise NearlinkBridgeError("device_not_connected", "The NearLink device is not connected.", status=409)
        return session

    def list_adapters(self) -> list[dict]:
        return deepcopy(self.adapters)

    def list_devices(self) -> list[dict]:
        return [deepcopy(item) for item in self.devices.values()]

    def get_device(self, device_key: str) -> dict:
        return deepcopy(self._require_device(device_key))

    async def start_discovery(self, payload: dict) -> dict:
        self._discovery_counter += 1
        discovery_id = f"discovery-{self._discovery_counter:04d}"
        filters = dict(payload.get("filters") or {})
        name_prefix = str(filters.get("name_prefix") or "").strip()
        product_codes = {str(item).strip() for item in filters.get("product_codes") or [] if str(item).strip()}
        items = []
        for device in self.devices.values():
            if name_prefix and not str(device.get("display_name") or "").startswith(name_prefix):
                continue
            if product_codes and str(device.get("product_code") or "") not in product_codes:
                continue
            record = deepcopy(device)
            record["discovered_at"] = self._timestamp()
            items.append(record)
        session = {
            "discovery_id": discovery_id,
            "status": "completed",
            "timeout_seconds": int(payload.get("timeout_seconds") or self.bridge_config.get("discovery", {}).get("default_timeout_seconds", 5)),
            "started_at": self._timestamp(),
            "finished_at": self._timestamp(),
            "filters": deepcopy(filters),
            "devices": items,
        }
        self.discovery_sessions[discovery_id] = session
        return deepcopy(session)

    def stop_discovery(self, discovery_id: str) -> dict:
        session = self.discovery_sessions.get(discovery_id)
        if session is None:
            raise NearlinkBridgeError("discovery_not_found", "The discovery session was not found.", status=404)
        session["status"] = "stopped"
        session["finished_at"] = self._timestamp()
        return deepcopy(session)

    def get_discovery(self, discovery_id: str) -> dict:
        session = self.discovery_sessions.get(discovery_id)
        if session is None:
            raise NearlinkBridgeError("discovery_not_found", "The discovery session was not found.", status=404)
        return deepcopy(session)

    async def connect_device(self, device_key: str) -> dict:
        device = self._require_device(device_key)
        max_devices = int(self.bridge_config.get("sessions", {}).get("max_active_devices", 100))
        if len(self.sessions) >= max_devices and device_key not in self.sessions:
            raise NearlinkBridgeError("session_limit_reached", "The active NearLink session limit has been reached.", status=409)
        session = {
            "device_key": device_key,
            "status": "connected",
            "connected_at": self._timestamp(),
        }
        self.sessions[device_key] = session
        device["state"]["online"] = True
        if self.callback_client is not None:
            await self.callback_client.post_bridge_event(
                {
                    "bridge_type": "nearlink",
                    "bridge_id": self.bridge_id,
                    "device_key": device_key,
                    "event_type": "nearlink.state.changed",
                    "timestamp": self._timestamp(),
                    "payload": {"online": True, "signal_strength": device.get("signal_strength")},
                }
            )
        return deepcopy(session)

    async def disconnect_device(self, device_key: str) -> dict:
        self._require_device(device_key)
        self.sessions.pop(device_key, None)
        self.devices[device_key]["state"]["online"] = False
        result = {"device_key": device_key, "status": "disconnected", "disconnected_at": self._timestamp()}
        if self.callback_client is not None:
            await self.callback_client.post_bridge_event(
                {
                    "bridge_type": "nearlink",
                    "bridge_id": self.bridge_id,
                    "device_key": device_key,
                    "event_type": "nearlink.state.changed",
                    "timestamp": self._timestamp(),
                    "payload": {"online": False},
                }
            )
        return result

    async def command_device(self, device_key: str, payload: dict) -> dict:
        self._require_session(device_key)
        state = self.devices[device_key]["state"]
        arguments = dict(payload.get("arguments") or {})
        if payload.get("action") in {"turn_on", "enable"}:
            state["online"] = True
        if payload.get("action") in {"turn_off", "disable"}:
            state["online"] = False
        if "target_state" in arguments:
            state["target_state"] = arguments["target_state"]
        result = {
            "device_key": device_key,
            "command_type": payload.get("command_type") or "capability.invoke",
            "capability_code": payload.get("capability_code"),
            "action": payload.get("action"),
            "arguments": arguments,
            "executed_at": self._timestamp(),
            "state": deepcopy(state),
        }
        if self.callback_client is not None:
            await self.callback_client.post_command_result(
                {
                    "request_id": payload.get("request_id"),
                    "gateway_id": payload.get("gateway_id"),
                    "adapter_type": "nearlink",
                    "status": "succeeded",
                    "result": {
                        "device_id": payload.get("device_id"),
                        "command_name": payload.get("action"),
                        "protocol_response": result,
                    },
                }
            )
        return result

    async def query_state(self, device_key: str, payload: dict) -> dict:
        self._require_session(device_key)
        state = deepcopy(self.devices[device_key]["state"])
        result = {
            "device_key": device_key,
            "query_type": payload.get("query_type") or "state",
            "queried_at": self._timestamp(),
            "state": state,
        }
        if self.callback_client is not None:
            await self.callback_client.post_http_push(
                {
                    "adapter_type": "sensor_http_push",
                    "device_id": payload.get("device_id") or device_key,
                    "gateway_id": payload.get("gateway_id") or self.bridge_id,
                    "discovery_id": f"nearlink:{self.bridge_id}:{device_key}",
                    "display_name": self.devices[device_key].get("display_name"),
                    "device_kind": self.devices[device_key].get("device_kind", "actuator"),
                    "protocol_type": "nearlink",
                    "observed_at": self._timestamp(),
                    "telemetry": deepcopy(state),
                }
            )
        return result
