from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from core.store.exceptions import DeviceBindException, DeviceNotFoundException


class LocalControlPlaneStore:
    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        (self.root_dir / "devices").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "agents").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "users").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "channels").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "user_device_mappings").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "user_channel_mappings").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "channel_device_mappings").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "device_agent_mappings").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "events").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "telemetry").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "alarms").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "gateways").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "capabilities").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "capability_routes").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "ota_firmwares").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "ota_campaigns").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "chat_history").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "chat_summaries").mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_config(cls, config: dict[str, Any], *, project_dir: str | Path | None = None):
        base_dir = Path(project_dir) if project_dir is not None else Path(__file__).resolve().parents[2]
        control_plane_config = config.get("control-plane", {})
        data_dir = control_plane_config.get("data_dir")
        root_dir = Path(data_dir) if data_dir else base_dir / "data" / "control_plane"
        return cls(root_dir)

    def load_server_profile(self) -> dict[str, Any]:
        return self._read_yaml(self.root_dir / "server.yaml", default={})

    def save_server_profile(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._write_yaml(self.root_dir / "server.yaml", payload)
        return payload

    def get_device(self, device_id: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "devices" / f"{device_id}.yaml")

    def save_device(self, device_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(payload)
        device_id = str(device_id or payload.get("device_id", "")).strip()
        if not device_id:
            raise ValueError("device_id_required")
        user_id = self._normalize_owner_user_id(payload.get("user_id"))
        record = dict(payload)
        record.setdefault("device_id", device_id)
        record["user_id"] = user_id
        record.setdefault("bind_status", "pending")
        record.setdefault("lifecycle_status", "created")
        record.setdefault("channel_ids", [])
        self._write_yaml(self.root_dir / "devices" / f"{device_id}.yaml", record)
        self._replace_user_device_mappings_for_device(user_id, device_id)
        return record

    def list_devices(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "devices")

    def claim_device(self, device_id: str, user_id: str) -> dict[str, Any]:
        device = self.get_device(device_id)
        if device is None:
            raise DeviceNotFoundException(device_id)
        normalized_user_id = self._normalize_owner_user_id(user_id)
        record = dict(device)
        record["user_id"] = normalized_user_id
        record["lifecycle_status"] = "claimed"
        self._write_yaml(self.root_dir / "devices" / f"{device_id}.yaml", record)
        self._replace_user_device_mappings_for_device(normalized_user_id, device_id)
        return record

    def bind_device(self, device_id: str, bind_code: str | None = None) -> dict[str, Any]:
        device = self.get_device(device_id)
        if device is None:
            raise DeviceNotFoundException(device_id)
        expected_bind_code = str(device.get("bind_code") or "").strip()
        provided_bind_code = str(bind_code or "").strip()
        if expected_bind_code and provided_bind_code and expected_bind_code != provided_bind_code:
            raise ValueError("bind_code_invalid")
        record = dict(device)
        record["bind_status"] = "bound"
        record["lifecycle_status"] = "bound"
        self._write_yaml(self.root_dir / "devices" / f"{device_id}.yaml", record)
        return record

    def suspend_device(self, device_id: str, reason: str | None = None) -> dict[str, Any]:
        device = self.get_device(device_id)
        if device is None:
            raise DeviceNotFoundException(device_id)
        record = dict(device)
        record["lifecycle_status"] = "suspended"
        if reason:
            record["suspend_reason"] = reason
        self._write_yaml(self.root_dir / "devices" / f"{device_id}.yaml", record)
        return record

    def retire_device(self, device_id: str, reason: str | None = None) -> dict[str, Any]:
        device = self.get_device(device_id)
        if device is None:
            raise DeviceNotFoundException(device_id)
        record = dict(device)
        record["lifecycle_status"] = "retired"
        if reason:
            record["retire_reason"] = reason
        self._write_yaml(self.root_dir / "devices" / f"{device_id}.yaml", record)
        return record

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "agents" / f"{agent_id}.yaml")

    def save_agent(self, agent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(payload)
        payload.setdefault("agent_id", agent_id)
        self._write_yaml(self.root_dir / "agents" / f"{agent_id}.yaml", payload)
        return payload

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "users" / f"{user_id}.yaml")

    def create_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(payload)
        user_id = str(payload.get("user_id", "")).strip()
        if not user_id:
            raise ValueError("user_id_required")
        payload.setdefault("status", "active")
        self._write_yaml(self.root_dir / "users" / f"{user_id}.yaml", payload)
        return payload

    def save_user(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        record = dict(self.get_user(user_id) or {})
        record.update(dict(payload))
        record["user_id"] = user_id
        record.setdefault("status", "active")
        self._write_yaml(self.root_dir / "users" / f"{user_id}.yaml", record)
        return record

    def list_users(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "users")

    def delete_user(self, user_id: str) -> bool:
        path = self.root_dir / "users" / f"{user_id}.yaml"
        if not path.exists():
            return False
        path.unlink()
        return True

    def ensure_anonymous_user(self) -> dict[str, Any]:
        payload = self.get_user("anonymous")
        if isinstance(payload, dict):
            return payload
        payload = {
            "user_id": "anonymous",
            "name": "Anonymous",
            "status": "active",
            "is_anonymous": True,
        }
        self._write_yaml(self.root_dir / "users" / "anonymous.yaml", payload)
        return payload

    def get_channel(self, channel_id: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "channels" / f"{channel_id}.yaml")

    def create_channel(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(payload)
        channel_id = str(payload.get("channel_id", "")).strip()
        if not channel_id:
            raise ValueError("channel_id_required")
        user_id = self._normalize_owner_user_id(payload.get("user_id"))
        record = dict(payload)
        record["user_id"] = user_id
        record.setdefault("status", "active")
        self._write_yaml(self.root_dir / "channels" / f"{channel_id}.yaml", record)
        self._sync_user_channel_mapping(user_id, channel_id)
        return record

    def save_channel(self, channel_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        existing = self.get_channel(channel_id)
        if existing is None:
            raise ValueError("channel_not_found")
        user_id = self._normalize_owner_user_id(payload.get("user_id", existing.get("user_id")))
        record = dict(existing)
        record.update(dict(payload))
        record["channel_id"] = channel_id
        record["user_id"] = user_id
        record.setdefault("status", "active")
        self._write_yaml(self.root_dir / "channels" / f"{channel_id}.yaml", record)
        self._sync_user_channel_mapping(user_id, channel_id)
        return record

    def list_channels(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "channels")

    def delete_channel(self, channel_id: str) -> bool:
        path = self.root_dir / "channels" / f"{channel_id}.yaml"
        if not path.exists():
            return False
        path.unlink()
        return True

    def list_user_device_mappings(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "user_device_mappings")

    def save_user_device_mapping(self, mapping_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        mapping_id = str(mapping_id or payload.get("mapping_id", "")).strip()
        if not mapping_id:
            raise ValueError("mapping_id_required")
        user_id = self._normalize_owner_user_id(payload.get("user_id"))
        device_id = str(payload.get("device_id", "")).strip()
        if not device_id:
            raise ValueError("device_id_required")
        device = self.get_device(device_id)
        if device is None:
            raise ValueError("device_not_found")
        if str(device.get("user_id") or "") != user_id:
            raise ValueError("device_user_mismatch")
        record = {
            "mapping_id": mapping_id,
            "user_id": user_id,
            "device_id": device_id,
            "role": payload.get("role", "owner"),
            "enabled": payload.get("enabled", True),
        }
        self._write_yaml(self.root_dir / "user_device_mappings" / f"{mapping_id}.yaml", record)
        return record

    def list_user_channel_mappings(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "user_channel_mappings")

    def save_user_channel_mapping(self, mapping_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        mapping_id = str(mapping_id or payload.get("mapping_id", "")).strip()
        if not mapping_id:
            raise ValueError("mapping_id_required")
        user_id = self._normalize_owner_user_id(payload.get("user_id"))
        channel_id = str(payload.get("channel_id", "")).strip()
        if not channel_id:
            raise ValueError("channel_id_required")
        channel = self.get_channel(channel_id)
        if channel is None:
            raise ValueError("channel_not_found")
        if str(channel.get("user_id") or "") != user_id:
            raise ValueError("channel_user_mismatch")
        record = {
            "mapping_id": mapping_id,
            "user_id": user_id,
            "channel_id": channel_id,
            "role": payload.get("role", "owner"),
            "enabled": payload.get("enabled", True),
        }
        self._write_yaml(self.root_dir / "user_channel_mappings" / f"{mapping_id}.yaml", record)
        return record

    def list_channel_device_mappings(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "channel_device_mappings")

    def save_channel_device_mapping(self, mapping_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        mapping_id = str(mapping_id or payload.get("mapping_id", "")).strip()
        if not mapping_id:
            raise ValueError("mapping_id_required")
        channel_id = str(payload.get("channel_id", "")).strip()
        device_id = str(payload.get("device_id", "")).strip()
        if not channel_id:
            raise ValueError("channel_id_required")
        if not device_id:
            raise ValueError("device_id_required")
        channel = self.get_channel(channel_id)
        if channel is None:
            raise ValueError("channel_not_found")
        device = self.get_device(device_id)
        if device is None:
            raise ValueError("device_not_found")
        if str(channel.get("user_id") or "") != str(device.get("user_id") or ""):
            raise ValueError("channel_device_user_mismatch")
        record = {
            "mapping_id": mapping_id,
            "channel_id": channel_id,
            "device_id": device_id,
            "enabled": payload.get("enabled", True),
            "priority": payload.get("priority", 100),
        }
        self._write_yaml(self.root_dir / "channel_device_mappings" / f"{mapping_id}.yaml", record)
        return record

    def get_primary_channel_device_mapping(self, device_id: str) -> dict[str, Any] | None:
        for payload in self.list_channel_device_mappings():
            if payload.get("device_id") != device_id:
                continue
            if payload.get("enabled", True) is False:
                continue
            return payload
        return None

    def bind_device_agent(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(payload)
        mapping_id = str(payload.get("mapping_id", "")).strip()
        if not mapping_id:
            raise ValueError("mapping_id_required")
        device_id = str(payload.get("device_id", "")).strip()
        if not device_id:
            raise ValueError("device_id_required")
        if self.get_device(device_id) is None:
            raise ValueError("device_not_found")
        payload.setdefault("enabled", True)
        self._write_yaml(self.root_dir / "device_agent_mappings" / f"{mapping_id}.yaml", payload)
        return payload

    def list_device_agent_mappings(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "device_agent_mappings")

    def batch_import_devices(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        imported: list[dict[str, Any]] = []
        for payload in items:
            imported.append(self.save_device(payload.get("device_id"), payload))
        return imported

    def get_active_device_agent_mapping(self, device_id: str) -> dict[str, Any] | None:
        mappings_dir = self.root_dir / "device_agent_mappings"
        for path in sorted(mappings_dir.glob("*.yaml")):
            payload = self._read_yaml(path)
            if not isinstance(payload, dict):
                continue
            if payload.get("device_id") != device_id:
                continue
            if payload.get("enabled", True) is False:
                continue
            return payload
        return None

    def append_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(payload)
        event_id = str(payload.get("event_id", "")).strip()
        if not event_id:
            raise ValueError("event_id_required")
        self._write_yaml(self.root_dir / "events" / f"{event_id}.yaml", payload)

        alarm_id = str(payload.get("alarm_id", "")).strip()
        if payload.get("event_type") == "alarm.triggered" and alarm_id:
            self._write_yaml(
                self.root_dir / "alarms" / f"{alarm_id}.yaml",
                {
                    "alarm_id": alarm_id,
                    "device_id": payload.get("device_id"),
                    "message": payload.get("message"),
                    "status": "active",
                    "last_event_id": event_id,
                },
            )
        elif payload.get("event_type") == "alarm.cleared" and alarm_id:
            alarm = self._read_yaml(self.root_dir / "alarms" / f"{alarm_id}.yaml", default={}) or {}
            alarm["alarm_id"] = alarm_id
            alarm["status"] = "cleared"
            alarm["last_event_id"] = event_id
            self._write_yaml(self.root_dir / "alarms" / f"{alarm_id}.yaml", alarm)
        return payload

    def list_events(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "events")

    def append_telemetry(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(payload)
        telemetry_id = str(payload.get("telemetry_id", "")).strip()
        if not telemetry_id:
            raise ValueError("telemetry_id_required")
        self._write_yaml(self.root_dir / "telemetry" / f"{telemetry_id}.yaml", payload)
        return payload

    def list_telemetry(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "telemetry")

    def list_alarms(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "alarms")

    def acknowledge_alarm(self, alarm_id: str) -> dict[str, Any] | None:
        payload = self._read_yaml(self.root_dir / "alarms" / f"{alarm_id}.yaml")
        if not isinstance(payload, dict):
            return None
        payload["status"] = "acked"
        self._write_yaml(self.root_dir / "alarms" / f"{alarm_id}.yaml", payload)
        return payload

    def get_gateway(self, gateway_id: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "gateways" / f"{gateway_id}.yaml")

    def save_gateway(self, gateway_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        gateway_id = str(gateway_id or payload.get("gateway_id", "")).strip()
        if not gateway_id:
            raise ValueError("gateway_id_required")
        record = dict(payload)
        record.setdefault("gateway_id", gateway_id)
        self._write_yaml(self.root_dir / "gateways" / f"{gateway_id}.yaml", record)
        return record

    def list_gateways(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "gateways")

    def save_capability(self, capability_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        capability_id = str(capability_id or payload.get("capability_id", "")).strip()
        if not capability_id:
            raise ValueError("capability_id_required")
        record = dict(payload)
        record.setdefault("capability_id", capability_id)
        self._write_yaml(self.root_dir / "capabilities" / f"{capability_id}.yaml", record)
        return record

    def list_capabilities(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "capabilities")

    def save_capability_route(self, route_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        route_id = str(route_id or payload.get("route_id", "")).strip()
        if not route_id:
            raise ValueError("route_id_required")
        record = dict(payload)
        record.setdefault("route_id", route_id)
        self._write_yaml(self.root_dir / "capability_routes" / f"{route_id}.yaml", record)
        return record

    def list_capability_routes(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "capability_routes")

    def get_firmware(self, firmware_id: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "ota_firmwares" / f"{firmware_id}.yaml")

    def save_firmware(self, firmware_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        firmware_id = str(firmware_id or payload.get("firmware_id", "")).strip()
        if not firmware_id:
            raise ValueError("firmware_id_required")
        record = dict(payload)
        record.setdefault("firmware_id", firmware_id)
        self._write_yaml(self.root_dir / "ota_firmwares" / f"{firmware_id}.yaml", record)
        return record

    def list_firmwares(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "ota_firmwares")

    def save_ota_campaign(self, campaign_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        campaign_id = str(campaign_id or payload.get("campaign_id", "")).strip()
        if not campaign_id:
            raise ValueError("campaign_id_required")
        record = dict(payload)
        record.setdefault("campaign_id", campaign_id)
        self._write_yaml(self.root_dir / "ota_campaigns" / f"{campaign_id}.yaml", record)
        return record

    def list_ota_campaigns(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "ota_campaigns")

    def load_chat_history(self, session_id: str) -> list[dict[str, Any]]:
        records = self._read_yaml(
            self.root_dir / "chat_history" / f"{session_id}.yaml",
            default=[],
        )
        return records if isinstance(records, list) else []

    def append_chat_history(self, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        record = dict(payload)
        record.setdefault("session_id", session_id)
        records = self.load_chat_history(session_id)
        records.append(record)
        self._write_yaml(self.root_dir / "chat_history" / f"{session_id}.yaml", records)
        return record

    def get_summary_request(self, summary_id: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "chat_summaries" / f"{summary_id}.yaml")

    def save_summary_request(self, summary_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        record = dict(payload)
        record.setdefault("summary_id", summary_id)
        self._write_yaml(self.root_dir / "chat_summaries" / f"{summary_id}.yaml", record)
        return record

    def build_server_config(self, base_config: dict[str, Any]) -> dict[str, Any]:
        server_profile = self.load_server_profile()
        return self._deep_merge(base_config, server_profile)

    def resolve_device_config(
        self,
        base_config: dict[str, Any],
        device_id: str,
        client_id: str | None,
        selected_module: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        device = self.get_device(device_id)
        if device is None:
            raise DeviceNotFoundException(device_id)

        bind_status = str(device.get("bind_status", "pending")).lower()
        bind_code = device.get("bind_code") or ""
        if bind_status != "bound":
            raise DeviceBindException(bind_code)

        resolved_config = self.build_server_config(base_config)
        binding = self.get_active_device_agent_mapping(device_id) or {}
        agent_id = str(binding.get("agent_id") or device.get("agent_id") or "default")
        agent = self.get_agent(agent_id) or {"agent_id": agent_id}

        resolved_config = self._deep_merge(resolved_config, agent)
        resolved_config = self._deep_merge(
            resolved_config,
            device.get("runtime_overrides") or {},
        )
        if selected_module:
            resolved_config.setdefault("selected_module", {})
            resolved_config["selected_module"] = self._deep_merge(
                resolved_config["selected_module"],
                selected_module,
            )

        return {
            "device": {
                "device_id": device_id,
                "client_id": client_id,
                "agent_id": agent_id,
                "bind_status": bind_status,
                "bind_code": bind_code or None,
            },
            "binding": deepcopy(binding),
            "agent": {
                "agent_id": agent_id,
                "prompt": resolved_config.get("prompt"),
                "prompt_template": resolved_config.get("prompt_template"),
                "modules": deepcopy(resolved_config.get("selected_module", {})),
            },
            "resolved_config": resolved_config,
        }

    def build_runtime_binding_view(self, device_id: str) -> dict[str, Any]:
        device = self.get_device(device_id)
        if device is None:
            raise DeviceNotFoundException(device_id)
        device_agent_mapping = self.get_active_device_agent_mapping(device_id) or {}
        channel_device_mapping = self.get_primary_channel_device_mapping(device_id) or {}
        return {
            "device_id": device_id,
            "user_id": device.get("user_id"),
            "channel_id": channel_device_mapping.get("channel_id"),
            "agent_id": device_agent_mapping.get("agent_id") or device.get("agent_id"),
            "model_provider_id": None,
            "model_config_id": None,
            "knowledge_ids": [],
            "workflow_ids": [],
            "gateway_ids": [device.get("gateway_id")] if device.get("gateway_id") else [],
            "runtime_overrides": deepcopy(device.get("runtime_overrides") or {}),
        }

    def build_runtime_capability_routing_view(self, device_id: str) -> dict[str, Any]:
        device = self.get_device(device_id)
        if device is None:
            raise DeviceNotFoundException(device_id)
        capability_refs = list(device.get("capability_refs") or [])
        routes: list[dict[str, Any]] = []
        for route in self.list_capability_routes():
            capability_code = route.get("capability_code")
            if capability_code not in capability_refs:
                continue
            routes.append(
                {
                    "route_id": route.get("route_id"),
                    "capability_code": capability_code,
                    "gateway_id": route.get("gateway_id") or device.get("gateway_id"),
                    "protocol_type": route.get("protocol_type"),
                }
            )
        return {
            "device_id": device_id,
            "device_type": device.get("device_type"),
            "gateway_id": device.get("gateway_id"),
            "capability_refs": capability_refs,
            "command_routes": routes,
        }

    def _read_yaml(self, path: Path, default: dict[str, Any] | None = None) -> dict[str, Any] | None:
        if not path.exists():
            return deepcopy(default) if default is not None else None
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data is None:
            return deepcopy(default) if default is not None else None
        return data

    def _write_yaml(self, path: Path, payload: dict[str, Any]):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def _deep_merge(self, base: Any, overlay: Any):
        if not isinstance(base, dict) or not isinstance(overlay, dict):
            return deepcopy(overlay)

        merged = deepcopy(base)
        for key, value in overlay.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = deepcopy(value)
        return merged

    def _list_yaml_dir(self, path: Path) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for file_path in sorted(path.glob("*.yaml")):
            payload = self._read_yaml(file_path)
            if isinstance(payload, dict):
                items.append(payload)
        return items

    def _normalize_owner_user_id(self, user_id: Any) -> str:
        normalized = str(user_id or "").strip()
        if not normalized:
            self.ensure_anonymous_user()
            return "anonymous"
        if normalized == "anonymous":
            self.ensure_anonymous_user()
            return normalized
        if self.get_user(normalized) is None:
            raise ValueError("user_not_found")
        return normalized

    def _sync_user_device_mapping(self, user_id: str, device_id: str):
        mapping_id = f"user-device-{user_id}-{device_id}"
        self._write_yaml(
            self.root_dir / "user_device_mappings" / f"{mapping_id}.yaml",
            {
                "mapping_id": mapping_id,
                "user_id": user_id,
                "device_id": device_id,
                "role": "owner",
                "enabled": True,
            },
        )

    def _replace_user_device_mappings_for_device(self, user_id: str, device_id: str):
        for path in (self.root_dir / "user_device_mappings").glob("*.yaml"):
            payload = self._read_yaml(path)
            if isinstance(payload, dict) and payload.get("device_id") == device_id:
                path.unlink(missing_ok=True)
        self._sync_user_device_mapping(user_id, device_id)

    def _sync_user_channel_mapping(self, user_id: str, channel_id: str):
        mapping_id = f"user-channel-{user_id}-{channel_id}"
        self._write_yaml(
            self.root_dir / "user_channel_mappings" / f"{mapping_id}.yaml",
            {
                "mapping_id": mapping_id,
                "user_id": user_id,
                "channel_id": channel_id,
                "role": "owner",
                "enabled": True,
            },
        )
