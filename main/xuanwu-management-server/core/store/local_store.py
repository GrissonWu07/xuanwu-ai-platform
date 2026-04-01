from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yaml

from core.store.exceptions import DeviceBindException, DeviceNotFoundException


class LocalControlPlaneStore:
    DEFAULT_ROLE_DEFINITIONS = [
        {
            "role_id": "owner",
            "display_label": "Owner",
            "description": "Full ownership for personal devices, agents, and automations.",
            "permissions": [
                "devices.read",
                "devices.write",
                "agents.read",
                "agents.write",
                "jobs.read",
                "jobs.write",
                "alerts.read",
                "alerts.ack",
                "users.read",
                "channels.read",
                "channels.write",
            ],
        },
        {
            "role_id": "operator",
            "display_label": "Operator",
            "description": "Operate devices and acknowledge alerts without ownership changes.",
            "permissions": [
                "devices.read",
                "devices.write",
                "jobs.read",
                "jobs.write",
                "alerts.read",
                "alerts.ack",
                "channels.read",
            ],
        },
        {
            "role_id": "viewer",
            "display_label": "Viewer",
            "description": "Read-only access for dashboards, device state, and jobs.",
            "permissions": [
                "devices.read",
                "jobs.read",
                "alerts.read",
                "channels.read",
            ],
        },
    ]

    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        (self.root_dir / "devices").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "agents").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "users").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "roles").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "channels").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "discovered_devices").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "user_device_mappings").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "user_channel_mappings").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "channel_device_mappings").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "device_agent_mappings").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "agent_model_provider_mappings").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "agent_model_config_mappings").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "agent_knowledge_mappings").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "agent_workflow_mappings").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "events").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "telemetry").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "alarms").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "gateways").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "capabilities").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "capability_routes").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "ota_firmwares").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "ota_campaigns").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "auth_sessions").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "command_results").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "chat_history").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "chat_summaries").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "job_schedules").mkdir(parents=True, exist_ok=True)
        (self.root_dir / "job_runs").mkdir(parents=True, exist_ok=True)

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
        record.setdefault("device_kind", "conversational")
        record.setdefault("ingress_type", "device_server")
        record.setdefault("bind_status", "pending")
        record.setdefault("lifecycle_status", "created")
        record.setdefault("channel_ids", [])
        record.setdefault("gateway_id", None)
        record.setdefault("protocol_type", None)
        record.setdefault("adapter_type", None)
        record.setdefault("runtime_endpoint", None)
        record.setdefault("capability_refs", [])
        record.setdefault("runtime_overrides", {})
        record.setdefault("connection_status", "unknown")
        record.setdefault("session_status", "unknown")
        record.setdefault("last_seen_at", None)
        record.setdefault("last_event_at", None)
        record.setdefault("last_telemetry_at", None)
        record.setdefault("last_command_at", None)
        self._write_yaml(self.root_dir / "devices" / f"{device_id}.yaml", record)
        self._replace_user_device_mappings_for_device(user_id, device_id)
        return record

    def list_devices(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "devices")

    def get_discovered_device(self, discovery_id: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "discovered_devices" / f"{discovery_id}.yaml")

    def list_discovered_devices(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "discovered_devices")

    def save_discovered_device(self, discovery_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        record = dict(payload)
        discovery_id = str(discovery_id or record.get("discovery_id", "")).strip()
        device_id = str(record.get("device_id", "")).strip()
        if not discovery_id:
            raise ValueError("discovery_id_required")
        if not device_id:
            raise ValueError("device_id_required")
        existing = self.get_discovered_device(discovery_id) or {}
        merged = dict(existing)
        merged.update(record)
        merged["discovery_id"] = discovery_id
        merged["device_id"] = device_id
        merged.setdefault("ingress_type", "gateway")
        merged.setdefault("device_kind", "sensor")
        merged.setdefault("gateway_id", None)
        merged.setdefault("protocol_type", None)
        merged.setdefault("adapter_type", None)
        merged.setdefault("runtime_endpoint", None)
        merged.setdefault("source_payload", {})
        merged.setdefault("first_seen_at", merged.get("last_seen_at"))
        merged.setdefault("last_seen_at", merged.get("first_seen_at"))
        merged.setdefault("discovery_status", "pending")
        self._write_yaml(self.root_dir / "discovered_devices" / f"{discovery_id}.yaml", merged)
        return merged

    def promote_discovered_device(self, discovery_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        discovered = self.get_discovered_device(discovery_id)
        if discovered is None:
            raise ValueError("discovered_device_not_found")
        device_payload = {
            "device_id": discovered["device_id"],
            "user_id": payload.get("user_id"),
            "display_name": payload.get("display_name"),
            "device_kind": discovered.get("device_kind"),
            "ingress_type": discovered.get("ingress_type"),
            "gateway_id": discovered.get("gateway_id"),
            "protocol_type": discovered.get("protocol_type"),
            "adapter_type": discovered.get("adapter_type"),
            "runtime_endpoint": discovered.get("runtime_endpoint"),
            "bind_status": payload.get("bind_status", "pending"),
            "lifecycle_status": payload.get("lifecycle_status", "claimed"),
            "source_payload": deepcopy(discovered.get("source_payload") or {}),
            "last_seen_at": discovered.get("last_seen_at"),
        }
        saved = self.save_device(discovered["device_id"], device_payload)
        discovered_record = dict(discovered)
        discovered_record["discovery_status"] = "promoted"
        discovered_record["promoted_device_id"] = discovered["device_id"]
        self._write_yaml(self.root_dir / "discovered_devices" / f"{discovery_id}.yaml", discovered_record)
        return saved

    def ignore_discovered_device(self, discovery_id: str, reason: str | None = None) -> dict[str, Any]:
        discovered = self.get_discovered_device(discovery_id)
        if discovered is None:
            raise ValueError("discovered_device_not_found")
        updated = dict(discovered)
        updated["discovery_status"] = "ignored"
        if reason:
            updated["ignore_reason"] = reason
        self._write_yaml(self.root_dir / "discovered_devices" / f"{discovery_id}.yaml", updated)
        return updated

    def update_device_heartbeat(self, device_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        device = self.get_device(device_id)
        if device is None:
            raise DeviceNotFoundException(device_id)
        updated = dict(device)
        updated["connection_status"] = payload.get("status", updated.get("connection_status", "unknown"))
        updated["session_status"] = payload.get("session_status", updated.get("session_status"))
        updated["last_seen_at"] = payload.get("last_seen_at", updated.get("last_seen_at"))
        if payload.get("ingress_type"):
            updated["ingress_type"] = payload.get("ingress_type")
        if payload.get("gateway_id"):
            updated["gateway_id"] = payload.get("gateway_id")
        if payload.get("protocol_type"):
            updated["protocol_type"] = payload.get("protocol_type")
        if payload.get("adapter_type"):
            updated["adapter_type"] = payload.get("adapter_type")
        if payload.get("device_kind"):
            updated["device_kind"] = payload.get("device_kind")
        if payload.get("runtime_endpoint"):
            updated["runtime_endpoint"] = payload.get("runtime_endpoint")
        self._write_yaml(self.root_dir / "devices" / f"{device_id}.yaml", updated)
        return updated

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

    def create_auth_session(self, user_id: str, password: str | None) -> dict[str, Any]:
        user = self.get_user(user_id)
        if user is None:
            raise ValueError("user_not_found")
        expected_password = str(user.get("password") or "").strip()
        provided_password = str(password or "").strip()
        if expected_password and expected_password != provided_password:
            raise ValueError("password_invalid")
        token = f"session-{user_id}"
        record = {
            "session_token": token,
            "user_id": user_id,
            "status": "active",
            "issued_at": self._format_timestamp(datetime.now(timezone.utc)),
        }
        self._write_yaml(self.root_dir / "auth_sessions" / f"{token}.yaml", record)
        return record

    def get_auth_session(self, session_token: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "auth_sessions" / f"{session_token}.yaml")

    def delete_auth_session(self, session_token: str) -> bool:
        path = self.root_dir / "auth_sessions" / f"{session_token}.yaml"
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
            "role_ids": ["viewer"],
        }
        self._write_yaml(self.root_dir / "users" / "anonymous.yaml", payload)
        return payload

    def get_role(self, role_id: str) -> dict[str, Any] | None:
        payload = self._read_yaml(self.root_dir / "roles" / f"{role_id}.yaml")
        if isinstance(payload, dict):
            return payload
        for item in self.DEFAULT_ROLE_DEFINITIONS:
            if item["role_id"] == role_id:
                return deepcopy(item)
        return None

    def save_role(self, role_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        role_id = str(role_id or payload.get("role_id", "")).strip()
        if not role_id:
            raise ValueError("role_id_required")
        record = dict(payload)
        record["role_id"] = role_id
        record.setdefault("display_label", role_id.replace("-", " ").title())
        record.setdefault("description", "")
        record.setdefault("permissions", [])
        self._write_yaml(self.root_dir / "roles" / f"{role_id}.yaml", record)
        return record

    def list_roles(self) -> list[dict[str, Any]]:
        items = self._list_yaml_dir(self.root_dir / "roles")
        if items:
            return items
        return [deepcopy(item) for item in self.DEFAULT_ROLE_DEFINITIONS]

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

    def save_agent_model_provider_mapping(self, mapping_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        record = self._save_mapping_record(
            self.root_dir / "agent_model_provider_mappings",
            mapping_id,
            payload,
            required_key="model_provider_id",
        )
        return record

    def list_agent_model_provider_mappings(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "agent_model_provider_mappings")

    def save_agent_model_config_mapping(self, mapping_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._save_mapping_record(
            self.root_dir / "agent_model_config_mappings",
            mapping_id,
            payload,
            required_key="model_config_id",
        )

    def list_agent_model_config_mappings(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "agent_model_config_mappings")

    def save_agent_knowledge_mapping(self, mapping_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._save_mapping_record(
            self.root_dir / "agent_knowledge_mappings",
            mapping_id,
            payload,
            required_key="knowledge_id",
        )

    def list_agent_knowledge_mappings(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "agent_knowledge_mappings")

    def save_agent_workflow_mapping(self, mapping_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._save_mapping_record(
            self.root_dir / "agent_workflow_mappings",
            mapping_id,
            payload,
            required_key="workflow_id",
        )

    def list_agent_workflow_mappings(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "agent_workflow_mappings")

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
        self._touch_device_from_record(
            str(payload.get("device_id") or "").strip(),
            "last_event_at",
            payload.get("occurred_at") or payload.get("timestamp"),
        )

        alarm_id = str(payload.get("alarm_id", "")).strip()
        if payload.get("event_type") == "alarm.triggered" and alarm_id:
            alarm_source = (
                payload.get("source")
                or (payload.get("payload") or {}).get("source")
                or payload.get("device_id")
                or payload.get("gateway_id")
            )
            self._write_yaml(
                self.root_dir / "alarms" / f"{alarm_id}.yaml",
                {
                    "alarm_id": alarm_id,
                    "device_id": payload.get("device_id"),
                    "gateway_id": payload.get("gateway_id"),
                    "message": payload.get("message") or (payload.get("payload") or {}).get("message"),
                    "severity": payload.get("severity"),
                    "source": alarm_source,
                    "site_id": payload.get("site_id"),
                    "status": "active",
                    "created_at": payload.get("occurred_at") or payload.get("timestamp"),
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

    def list_events(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        items = self._list_yaml_dir(self.root_dir / "events")
        return self._filter_records(items, filters)

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "events" / f"{event_id}.yaml")

    def append_telemetry(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(payload)
        telemetry_id = str(payload.get("telemetry_id", "")).strip()
        if not telemetry_id:
            raise ValueError("telemetry_id_required")
        self._write_yaml(self.root_dir / "telemetry" / f"{telemetry_id}.yaml", payload)
        self._touch_device_from_record(
            str(payload.get("device_id") or "").strip(),
            "last_telemetry_at",
            payload.get("observed_at") or payload.get("reported_at") or payload.get("timestamp"),
        )
        return payload

    def list_telemetry(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        items = self._list_yaml_dir(self.root_dir / "telemetry")
        return self._filter_records(items, filters)

    def save_command_result(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(payload)
        result_id = str(payload.get("result_id", "")).strip()
        if not result_id:
            raise ValueError("result_id_required")
        self._write_yaml(self.root_dir / "command_results" / f"{result_id}.yaml", payload)
        self._touch_device_from_record(
            str(payload.get("device_id") or "").strip(),
            "last_command_at",
            payload.get("finished_at") or payload.get("timestamp"),
        )
        self.append_event(
            {
                "event_id": f"evt-{result_id}",
                "trace_id": payload.get("trace_id"),
                "device_id": payload.get("device_id"),
                "gateway_id": payload.get("gateway_id"),
                "event_type": "command.result",
                "severity": "info",
                "payload": {
                    "command_id": payload.get("command_id") or payload.get("request_id"),
                    "request_id": payload.get("request_id"),
                    "status": payload.get("status"),
                    "result": payload.get("result"),
                },
            }
        )
        return payload

    def list_alarms(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "alarms")

    def get_alarm(self, alarm_id: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "alarms" / f"{alarm_id}.yaml")

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

    def get_schedule(self, schedule_id: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "job_schedules" / f"{schedule_id}.yaml")

    def save_schedule(self, schedule_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        record = dict(payload)
        schedule_id = str(schedule_id or record.get("schedule_id", "")).strip()
        if not schedule_id:
            raise ValueError("schedule_id_required")
        record["schedule_id"] = schedule_id
        record.setdefault("enabled", True)
        record.setdefault("timezone", "UTC")
        record.setdefault("payload", {})
        record.setdefault("executor_type", "platform")
        record.setdefault("misfire_policy", "run_once")
        record.setdefault("misfire_grace_seconds", 0)
        record.setdefault("retry_policy", "never")
        record.setdefault("max_retry_attempts", 0)
        record.setdefault("retry_backoff_seconds", 0)
        record["status"] = "active" if record.get("enabled", True) else "disabled"
        self._write_yaml(self.root_dir / "job_schedules" / f"{schedule_id}.yaml", record)
        return record

    def list_schedules(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "job_schedules")

    def list_due_schedules(self, now_iso: str, *, limit: int = 100) -> list[dict[str, Any]]:
        now = self._parse_timestamp(now_iso)
        due_items: list[dict[str, Any]] = []
        for item in self.list_schedules():
            if not item.get("enabled", True):
                continue
            next_run_at = str(item.get("next_run_at") or "").strip()
            if not next_run_at:
                continue
            if self._parse_timestamp(next_run_at) <= now:
                due_items.append(item)
        due_items.sort(key=lambda item: str(item.get("next_run_at", "")))
        return due_items[:limit]

    def get_job_run(self, job_run_id: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "job_runs" / f"{job_run_id}.yaml")

    def list_job_runs(self) -> list[dict[str, Any]]:
        return self._list_yaml_dir(self.root_dir / "job_runs")

    def list_dispatchable_job_runs(self, now_iso: str, *, limit: int = 100) -> list[dict[str, Any]]:
        now = self._parse_timestamp(now_iso)
        dispatchable: list[dict[str, Any]] = []
        for item in self.list_job_runs():
            if str(item.get("status") or "").strip().lower() != "queued":
                continue
            scheduled_for = str(item.get("scheduled_for") or "").strip()
            if not scheduled_for:
                continue
            if self._parse_timestamp(scheduled_for) <= now:
                dispatchable.append(item)
        dispatchable.sort(key=lambda item: str(item.get("scheduled_for", "")))
        return dispatchable[:limit]

    def claim_schedule(self, schedule_id: str, scheduled_for: str) -> dict[str, Any]:
        schedule = self.get_schedule(schedule_id)
        if schedule is None:
            raise ValueError("schedule_not_found")
        if not schedule.get("enabled", True):
            raise ValueError("schedule_disabled")
        current_next_run = str(schedule.get("next_run_at") or "").strip()
        if not current_next_run:
            raise ValueError("next_run_at_required")
        if self._parse_timestamp(current_next_run) > self._parse_timestamp(scheduled_for):
            raise ValueError("schedule_not_due")

        job_run_id = self._build_job_run_id(schedule_id, scheduled_for)
        run_record = {
            "job_run_id": job_run_id,
            "schedule_id": schedule_id,
            "job_type": schedule.get("job_type"),
            "executor_type": schedule.get("executor_type"),
            "scheduled_for": scheduled_for,
            "status": "queued",
            "attempt": 1,
            "misfire_policy": schedule.get("misfire_policy", "run_once"),
            "misfire_grace_seconds": int(schedule.get("misfire_grace_seconds", 0) or 0),
            "retry_policy": schedule.get("retry_policy", "never"),
            "max_retry_attempts": int(schedule.get("max_retry_attempts", 0) or 0),
            "retry_backoff_seconds": int(schedule.get("retry_backoff_seconds", 0) or 0),
            "payload": deepcopy(schedule.get("payload") or {}),
        }
        self._write_yaml(self.root_dir / "job_runs" / f"{job_run_id}.yaml", run_record)

        updated_schedule = dict(schedule)
        updated_schedule["last_run_at"] = scheduled_for
        updated_schedule["next_run_at"] = self._calculate_next_run_at(updated_schedule, scheduled_for)
        self._write_yaml(
            self.root_dir / "job_schedules" / f"{schedule_id}.yaml",
            updated_schedule,
        )
        return run_record

    def claim_job_run(self, job_run_id: str, started_at: str) -> dict[str, Any]:
        existing = self.get_job_run(job_run_id)
        if existing is None:
            raise ValueError("job_run_not_found")
        if str(existing.get("status") or "").strip().lower() != "queued":
            raise ValueError("job_run_not_dispatchable")
        record = dict(existing)
        record["status"] = "running"
        record["started_at"] = started_at
        self._write_yaml(self.root_dir / "job_runs" / f"{job_run_id}.yaml", record)
        return record

    def pause_schedule(self, schedule_id: str, reason: str | None = None) -> dict[str, Any]:
        schedule = self.get_schedule(schedule_id)
        if schedule is None:
            raise ValueError("schedule_not_found")
        updated_schedule = dict(schedule)
        updated_schedule["enabled"] = False
        updated_schedule["status"] = "disabled"
        if reason:
            updated_schedule["pause_reason"] = reason
        self._write_yaml(self.root_dir / "job_schedules" / f"{schedule_id}.yaml", updated_schedule)
        return updated_schedule

    def resume_schedule(self, schedule_id: str, reason: str | None = None) -> dict[str, Any]:
        schedule = self.get_schedule(schedule_id)
        if schedule is None:
            raise ValueError("schedule_not_found")
        updated_schedule = dict(schedule)
        updated_schedule["enabled"] = True
        updated_schedule["status"] = "active"
        if reason:
            updated_schedule["resume_reason"] = reason
        self._write_yaml(self.root_dir / "job_schedules" / f"{schedule_id}.yaml", updated_schedule)
        return updated_schedule

    def trigger_schedule(self, schedule_id: str, scheduled_for: str) -> dict[str, Any]:
        schedule = self.get_schedule(schedule_id)
        if schedule is None:
            raise ValueError("schedule_not_found")
        return self._create_queued_job_run(schedule, scheduled_for, attempt=1, trigger_mode="manual")

    def complete_job_run(self, job_run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        existing = self.get_job_run(job_run_id)
        if existing is None:
            raise ValueError("job_run_not_found")
        record = dict(existing)
        record.update(dict(payload))
        record["job_run_id"] = job_run_id
        record["status"] = str(payload.get("status") or "completed")
        record.setdefault("finished_at", payload.get("finished_at") or record.get("finished_at"))
        self._write_yaml(self.root_dir / "job_runs" / f"{job_run_id}.yaml", record)
        return record

    def fail_job_run(self, job_run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        existing = self.get_job_run(job_run_id)
        if existing is None:
            raise ValueError("job_run_not_found")
        record = dict(existing)
        record.update(dict(payload))
        record["job_run_id"] = job_run_id
        record["status"] = str(payload.get("status") or "failed")
        failed_at = str(payload.get("failed_at") or record.get("failed_at") or record.get("scheduled_for") or "").strip()
        if failed_at:
            record["failed_at"] = failed_at
        retry_run = self._create_retry_job_run(record)
        if retry_run is not None:
            record["retry_status"] = "scheduled"
            record["retry_job_run_id"] = retry_run["job_run_id"]
        self._write_yaml(self.root_dir / "job_runs" / f"{job_run_id}.yaml", record)
        return record

    def retry_job_run(self, job_run_id: str, scheduled_for: str | None = None) -> dict[str, Any]:
        existing = self.get_job_run(job_run_id)
        if existing is None:
            raise ValueError("job_run_not_found")
        if str(existing.get("status") or "").strip().lower() not in {"failed", "completed"}:
            raise ValueError("job_run_not_retryable")
        schedule = self.get_schedule(str(existing.get("schedule_id") or ""))
        if schedule is None:
            raise ValueError("schedule_not_found")
        next_attempt = int(existing.get("attempt", 1) or 1) + 1
        when = str(scheduled_for or self._compute_retry_scheduled_for(existing)).strip()
        retry_run = self._create_queued_job_run(
            schedule,
            when,
            attempt=next_attempt,
            trigger_mode="retry",
        )
        updated_existing = dict(existing)
        updated_existing["retry_status"] = "scheduled"
        updated_existing["retry_job_run_id"] = retry_run["job_run_id"]
        self._write_yaml(self.root_dir / "job_runs" / f"{job_run_id}.yaml", updated_existing)
        return retry_run

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

    def build_auth_me(self, session_token: str) -> dict[str, Any] | None:
        session = self.get_auth_session(session_token)
        if session is None or str(session.get("status") or "").lower() != "active":
            return None
        user = self.get_user(str(session.get("user_id") or "").strip())
        if user is None:
            return None
        role_ids = list(user.get("role_ids") or [])
        permissions: set[str] = set()
        for role_id in role_ids:
            role = self.get_role(str(role_id))
            if role:
                permissions.update(str(item) for item in role.get("permissions") or [])
        return {
            "user_id": user["user_id"],
            "display_name": user.get("display_name") or user.get("name") or user["user_id"],
            "avatar_url": user.get("avatar_url"),
            "email": user.get("email"),
            "role_ids": role_ids,
            "permissions": sorted(permissions),
            "session_token": session_token,
            "session_status": session.get("status"),
            "is_anonymous": bool(user.get("is_anonymous")),
        }

    def build_dashboard_overview(self) -> dict[str, Any]:
        users = self.list_users()
        devices = self.list_devices()
        channels = self.list_channels()
        gateways = self.list_gateways()
        events = self.list_events()
        recent_events = self._sort_records_by_time(events, "occurred_at", "event_id", reverse=True)[:5]
        jobs_overview = self.build_jobs_overview()
        alerts_overview = self.build_alerts_overview()
        gateway_overview = self.build_gateway_overview()
        device_summary = self._build_device_summary(devices)
        active_device_agent_mappings = [
            item for item in self.list_device_agent_mappings() if item.get("enabled", True) is not False
        ]
        return {
            "hero": {
                "title": "Unified operations for every device surface",
                "subtitle": "Track ownership, active agents, schedules, and alerts from one calm control center.",
                "primaryAction": "Review device activity",
                "secondaryAction": "Inspect job health",
            },
            "statusPills": [
                {"label": "Healthy devices", "value": str(device_summary["lifecycle_counts"].get("bound", 0))},
                {"label": "Open alerts", "value": str(alerts_overview["ack_pending_count"])},
                {"label": "Queued jobs", "value": str(jobs_overview["running_count"])},
            ],
            "quickStats": [
                {
                    "id": "devices",
                    "label": "Devices",
                    "value": str(len(devices)),
                    "delta": f"{device_summary['bind_status_counts'].get('bound', 0)} bound",
                },
                {
                    "id": "agents",
                    "label": "Agents",
                    "value": str(len(active_device_agent_mappings)),
                    "delta": f"{len(active_device_agent_mappings)} active links",
                },
                {
                    "id": "jobs",
                    "label": "Jobs",
                    "value": str(len(jobs_overview["schedules"])),
                    "delta": f"{jobs_overview['running_count']} queued or running",
                },
                {
                    "id": "alerts",
                    "label": "Alerts",
                    "value": str(alerts_overview["ack_pending_count"]),
                    "delta": f"{alerts_overview['severity_counts'].get('critical', 0)} critical",
                },
            ],
            "todaySummary": [
                {"label": "Users", "value": str(len([item for item in users if item.get("user_id") != "anonymous"]))},
                {"label": "Channels", "value": str(len(channels))},
                {"label": "Gateways", "value": str(len(gateways))},
            ],
            "liveActivity": [
                {
                    "id": item.get("event_id"),
                    "title": item.get("message") or item.get("event_type") or item.get("event_id"),
                    "detail": item.get("source")
                    or item.get("device_id")
                    or item.get("gateway_id")
                    or item.get("event_type")
                    or "Platform event",
                    "at": item.get("occurred_at") or item.get("created_at") or item.get("timestamp"),
                    "to": self._build_portal_activity_target(item),
                }
                for item in recent_events
            ],
            "summary": {
                "user_count": len([item for item in users if item.get("user_id") != "anonymous"]),
                "device_count": len(devices),
                "channel_count": len(channels),
                "gateway_count": len(gateways),
            },
            "activity": recent_events,
            "device_summary": device_summary,
            "jobs_summary": jobs_overview,
            "alerts_summary": alerts_overview,
            "gateway_summary": gateway_overview,
        }

    def build_portal_config(self, config: dict[str, Any]) -> dict[str, Any]:
        server_profile = self.load_server_profile()
        return {
            "product": {
                "name": "XuanWu Portal",
                "default_tab": "overview",
            },
            "navigation": {
                "primary_tabs": ["overview", "devices", "agents", "jobs", "alerts"],
                "profile_menu": ["profile", "users", "channels", "gateways", "settings", "logout"],
            },
            "feature_flags": {
                "agents_proxy_enabled": True,
                "jobs_enabled": True,
                "alerts_enabled": True,
                "gateway_overview_enabled": True,
            },
            "visible_modules": [
                "overview",
                "devices",
                "agents",
                "jobs",
                "alerts",
                "users",
                "channels",
                "gateways",
            ],
            "upstream_status": {
                "management_server": "ready",
                "gateway": "ready" if self.list_gateways() else "empty",
                "jobs": "ready" if config.get("jobs") or server_profile.get("jobs") else "configured",
                "xuanwu": "proxy",
            },
            "documentation_links": {
                "blueprint": "/docs/superpowers/specs/2026-03-30-xuanwu-platform-blueprint.md",
                "api_completion": "/docs/superpowers/specs/2026-03-31-platform-api-completion-spec.md",
            },
            "environment": {
                "marker": config.get("env") or server_profile.get("environment") or "local",
                "management_api_base": "/control-plane/v1",
            },
        }

    def build_jobs_overview(self) -> dict[str, Any]:
        schedules = self.list_schedules()
        runs = self.list_job_runs()
        now = datetime.now(timezone.utc)
        running_statuses = {"queued", "running"}
        overdue_runs = [
            item
            for item in runs
            if str(item.get("status") or "").lower() in running_statuses
            and str(item.get("scheduled_for") or "").strip()
            and self._parse_timestamp(str(item["scheduled_for"])) <= now
        ]
        recent_failures = [
            item for item in self._sort_records_by_time(runs, "scheduled_for", "job_run_id", reverse=True)
            if str(item.get("status") or "").lower() == "failed"
        ][:5]
        executor_distribution: dict[str, int] = {}
        for item in schedules:
            executor_type = str(item.get("executor_type") or "platform")
            executor_distribution[executor_type] = executor_distribution.get(executor_type, 0) + 1
        sorted_schedules = self._sort_records_by_time(schedules, "next_run_at", "schedule_id")
        sorted_runs = self._sort_records_by_time(runs, "scheduled_for", "job_run_id", reverse=True)
        return {
            "summary": [
                {
                    "label": "Healthy schedules",
                    "value": str(len([item for item in schedules if item.get("enabled", True)])),
                },
                {"label": "Queued runs", "value": str(len(overdue_runs))},
                {
                    "label": "Success today",
                    "value": str(
                        len([item for item in runs if str(item.get("status") or "").lower() == "completed"])
                    ),
                },
            ],
            "schedules": [
                {
                    "schedule_id": item.get("schedule_id"),
                    "name": item.get("name") or item.get("schedule_id"),
                    "executor_type": item.get("executor_type"),
                    "schedule": item.get("cron") or item.get("schedule") or item.get("interval_seconds") or "manual",
                    "next_run_at": item.get("next_run_at"),
                    "status": "active" if item.get("enabled", True) else "disabled",
                }
                for item in sorted_schedules
            ],
            "runs": [
                {
                    "job_run_id": item.get("job_run_id"),
                    "schedule_id": item.get("schedule_id"),
                    "status": item.get("status"),
                    "executor_type": item.get("executor_type"),
                    "started_at": item.get("started_at"),
                    "finished_at": item.get("finished_at"),
                }
                for item in sorted_runs
            ],
            "scheduler_health": {
                "status": "ready",
                "enabled_schedule_count": len([item for item in schedules if item.get("enabled", True)]),
                "due_schedule_count": len(
                    [
                        item
                        for item in schedules
                        if item.get("enabled", True)
                        and str(item.get("next_run_at") or "").strip()
                        and self._parse_timestamp(str(item["next_run_at"])) <= now
                    ]
                ),
            },
            "running_count": len(
                [item for item in runs if str(item.get("status") or "").lower() in running_statuses]
            ),
            "recent_failures": recent_failures,
            "dispatch_lag": {
                "overdue_run_count": len(overdue_runs),
                "oldest_due_at": overdue_runs[0].get("scheduled_for") if overdue_runs else None,
            },
            "executor_distribution": executor_distribution,
        }

    def build_alerts_overview(self) -> dict[str, Any]:
        alarms = self.list_alarms()
        active_alarms = [
            item
            for item in alarms
            if str(item.get("status") or "").lower() not in {"acked", "cleared", "resolved"}
        ]
        severity_counts: dict[str, int] = {}
        source_counts: dict[str, int] = {}
        for item in active_alarms:
            severity = str(item.get("severity") or "unknown")
            source = str(item.get("source") or item.get("device_id") or "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1
        alarm_events = [item for item in self.list_events() if str(item.get("event_type") or "").startswith("alarm.")]
        reference_timestamp = next(
            (
                str(item.get("occurred_at") or item.get("timestamp") or "")
                for item in self._sort_records_by_time(alarm_events, "occurred_at", "event_id", reverse=True)
                if str(item.get("occurred_at") or item.get("timestamp") or "").strip()
            ),
            self._format_timestamp(datetime.now(timezone.utc)),
        )
        today_prefix = reference_timestamp[:10]
        escalated_today = len(
            [
                item
                for item in alarm_events
                if str(item.get("event_type") or "") == "alarm.escalated"
                and str(item.get("occurred_at") or item.get("timestamp") or "").startswith(today_prefix)
            ]
        )
        top_sources = [
            {"source": source, "count": count}
            for source, count in sorted(source_counts.items(), key=lambda item: (-item[1], item[0]))[:5]
        ]
        sorted_alarms = self._sort_records_by_time(alarms, "created_at", "alarm_id", reverse=True)
        alert_activity = self._sort_records_by_time(alarm_events, "occurred_at", "event_id", reverse=True)[:5]
        return {
            "summary": [
                {"label": "Active alerts", "value": str(len(active_alarms))},
                {
                    "label": "Acknowledged",
                    "value": str(
                        len([item for item in alarms if str(item.get("status") or "").lower() in {"acked", "acknowledged"}])
                    ),
                },
                {"label": "Critical", "value": str(severity_counts.get("critical", 0))},
            ],
            "alerts": [
                {
                    "alarm_id": item.get("alarm_id"),
                    "title": item.get("message") or item.get("source") or item.get("alarm_id"),
                    "severity": item.get("severity"),
                    "status": "acknowledged"
                    if str(item.get("status") or "").lower() == "acked"
                    else item.get("status"),
                    "source": item.get("source") or item.get("device_id") or item.get("gateway_id"),
                    "created_at": item.get("created_at"),
                }
                for item in sorted_alarms
            ],
            "activity": [
                {
                    "id": item.get("event_id"),
                    "title": item.get("message") or item.get("event_type") or item.get("event_id"),
                    "detail": item.get("source")
                    or item.get("device_id")
                    or item.get("gateway_id")
                    or item.get("alarm_id")
                    or "Alarm activity",
                    "at": item.get("occurred_at") or item.get("created_at") or item.get("timestamp"),
                    "to": self._build_portal_activity_target(item),
                }
                for item in alert_activity
            ],
            "severity_counts": severity_counts,
            "ack_pending_count": len(active_alarms),
            "escalated_today": escalated_today,
            "top_active_sources": top_sources,
        }

    def build_gateway_overview(self) -> dict[str, Any]:
        gateways = self.list_gateways()
        by_protocol: dict[str, int] = {}
        by_site: dict[str, int] = {}
        for item in gateways:
            protocol_type = str(item.get("protocol_type") or "unknown")
            site_id = str(item.get("site_id") or "unassigned")
            by_protocol[protocol_type] = by_protocol.get(protocol_type, 0) + 1
            by_site[site_id] = by_site.get(site_id, 0) + 1
        return {
            "total_count": len(gateways),
            "protocol_distribution": by_protocol,
            "site_distribution": by_site,
            "items": self._sort_records_by_time(gateways, "updated_at", "gateway_id", reverse=True)[:5],
        }

    def build_device_detail(self, device_id: str) -> dict[str, Any]:
        device = self.get_device(device_id)
        if device is None:
            raise DeviceNotFoundException(device_id)
        owner = self.get_user(str(device.get("user_id") or "anonymous"))
        discovery = self.get_discovered_device_for_device(device_id)
        gateway = self.get_gateway(str(device.get("gateway_id") or "")) if device.get("gateway_id") else None
        channel_memberships = [
            item
            for item in self.list_channel_device_mappings()
            if str(item.get("device_id") or "") == device_id and item.get("enabled", True)
        ]
        device_agent_mapping = self.get_active_device_agent_mapping(device_id)
        agent = None
        if device_agent_mapping:
            agent = self.get_agent(str(device_agent_mapping.get("agent_id") or ""))
        recent_events = self._sort_records_by_time(
            [item for item in self.list_events({"device_id": device_id})],
            "occurred_at",
            "event_id",
            reverse=True,
        )[:5]
        telemetry_items = self._sort_records_by_time(
            [item for item in self.list_telemetry({"device_id": device_id})],
            "observed_at",
            "telemetry_id",
            reverse=True,
        )
        latest_by_capability: dict[str, dict[str, Any]] = {}
        for item in telemetry_items:
            capability_code = str(item.get("capability_code") or "unknown")
            latest_by_capability.setdefault(capability_code, item)
        latest_command_result = self.get_latest_command_result_for_device(device_id)
        latest_alarm = self.get_latest_alarm_for_device(device_id)
        runtime_binding_view = self.build_runtime_binding_view(device_id)
        capability_routing_view = self.build_runtime_capability_routing_view(device_id)
        return {
            "device": deepcopy(device),
            "owner_summary": owner,
            "gateway_summary": gateway,
            "discovery": deepcopy(discovery or {}),
            "channel_memberships": channel_memberships,
            "agent_binding": {
                "mapping": deepcopy(device_agent_mapping or {}),
                "agent": deepcopy(agent or {}),
            },
            "runtime_binding_view": runtime_binding_view,
            "capability_routing_view": capability_routing_view,
            "binding": {
                "agent_id": runtime_binding_view.get("agent_id"),
                "channel_id": runtime_binding_view.get("channel_id"),
                "model_config_id": runtime_binding_view.get("model_config_id"),
            },
            "runtime": {
                "session_status": device.get("session_status"),
                "capability_route_count": len(capability_routing_view.get("command_routes") or []),
            },
            "recent_events": [
                {
                    "id": item.get("event_id"),
                    "title": item.get("message") or item.get("event_type") or item.get("event_id"),
                    "detail": item.get("source")
                    or item.get("device_id")
                    or item.get("gateway_id")
                    or item.get("event_type")
                    or "Device event",
                    "at": item.get("occurred_at") or item.get("timestamp"),
                }
                for item in recent_events
            ],
            "recent_telemetry": [
                {
                    "metric": item.get("capability_code"),
                    "value": json.dumps(item.get("metrics") or {}, ensure_ascii=False)
                    if isinstance(item.get("metrics"), dict)
                    else str(item.get("metrics") or item.get("value") or ""),
                    "at": item.get("observed_at") or item.get("reported_at") or item.get("timestamp"),
                }
                for item in list(latest_by_capability.values())
            ],
            "latest_telemetry_snapshot": list(latest_by_capability.values()),
            "latest_alarm": deepcopy(latest_alarm or {}),
            "latest_command_result": deepcopy(latest_command_result or {}),
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

    def get_discovered_device_for_device(self, device_id: str) -> dict[str, Any] | None:
        for item in self.list_discovered_devices():
            if str(item.get("device_id") or "") == device_id:
                return item
        return None

    def get_latest_command_result_for_device(self, device_id: str) -> dict[str, Any] | None:
        items = [
            item
            for item in self._list_yaml_dir(self.root_dir / "command_results")
            if str(item.get("device_id") or "") == device_id
        ]
        sorted_items = self._sort_records_by_time(items, "finished_at", "result_id", reverse=True)
        return sorted_items[0] if sorted_items else None

    def get_latest_alarm_for_device(self, device_id: str) -> dict[str, Any] | None:
        items = [
            item
            for item in self._list_yaml_dir(self.root_dir / "alarms")
            if str(item.get("device_id") or "") == device_id
        ]
        sorted_items = self._sort_records_by_time(items, "created_at", "alarm_id", reverse=True)
        return sorted_items[0] if sorted_items else None

    def _touch_device_from_record(self, device_id: str, field: str, timestamp: Any):
        if not device_id:
            return
        device = self.get_device(device_id)
        if device is None:
            return
        updated = dict(device)
        updated[field] = timestamp or updated.get(field)
        if field != "last_seen_at" and timestamp:
            updated["last_seen_at"] = timestamp
        self._write_yaml(self.root_dir / "devices" / f"{device_id}.yaml", updated)

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

    def _save_mapping_record(
        self,
        directory: Path,
        mapping_id: str,
        payload: dict[str, Any],
        *,
        required_key: str,
    ) -> dict[str, Any]:
        mapping_id = str(mapping_id or payload.get("mapping_id", "")).strip()
        if not mapping_id:
            raise ValueError("mapping_id_required")
        agent_id = str(payload.get("agent_id", "")).strip()
        if not agent_id:
            raise ValueError("agent_id_required")
        required_value = str(payload.get(required_key, "")).strip()
        if not required_value:
            raise ValueError(f"{required_key}_required")
        record = {
            "mapping_id": mapping_id,
            "agent_id": agent_id,
            required_key: required_value,
            "enabled": payload.get("enabled", True),
        }
        self._write_yaml(directory / f"{mapping_id}.yaml", record)
        return record

    def _filter_records(
        self, items: list[dict[str, Any]], filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        if not filters:
            return items
        normalized_filters = {
            key: str(value).strip()
            for key, value in filters.items()
            if value is not None and str(value).strip()
        }
        if not normalized_filters:
            return items

        def matches(item: dict[str, Any]) -> bool:
            tags = item.get("tags") if isinstance(item.get("tags"), dict) else {}
            for key, expected in normalized_filters.items():
                actual = item.get(key)
                if actual is None and key in tags:
                    actual = tags.get(key)
                if str(actual).strip() != expected:
                    return False
            return True

        return [item for item in items if matches(item)]

    def _sort_records_by_time(
        self,
        items: list[dict[str, Any]],
        primary_key: str,
        fallback_key: str,
        *,
        reverse: bool = False,
    ) -> list[dict[str, Any]]:
        def sort_key(item: dict[str, Any]):
            primary_value = str(
                item.get(primary_key)
                or item.get("updated_at")
                or item.get("created_at")
                or item.get("timestamp")
                or ""
            ).strip()
            try:
                parsed = self._parse_timestamp(primary_value) if primary_value else datetime.min.replace(tzinfo=timezone.utc)
            except Exception:
                parsed = datetime.min.replace(tzinfo=timezone.utc)
            return (parsed, str(item.get(fallback_key) or ""))

        return sorted(items, key=sort_key, reverse=reverse)

    def _build_device_summary(self, devices: list[dict[str, Any]]) -> dict[str, Any]:
        bind_status_counts: dict[str, int] = {}
        lifecycle_counts: dict[str, int] = {}
        for item in devices:
            bind_status = str(item.get("bind_status") or "unknown")
            lifecycle_status = str(item.get("lifecycle_status") or "unknown")
            bind_status_counts[bind_status] = bind_status_counts.get(bind_status, 0) + 1
            lifecycle_counts[lifecycle_status] = lifecycle_counts.get(lifecycle_status, 0) + 1
        return {
            "total_count": len(devices),
            "bind_status_counts": bind_status_counts,
            "lifecycle_counts": lifecycle_counts,
        }

    def _build_portal_activity_target(self, item: dict[str, Any]) -> str:
        alarm_id = str(item.get("alarm_id") or "").strip()
        if alarm_id:
            return f"/alerts?alarmId={alarm_id}"

        job_run_id = str(item.get("job_run_id") or "").strip()
        if job_run_id:
            return f"/jobs?jobRunId={job_run_id}"

        schedule_id = str(item.get("schedule_id") or "").strip()
        if schedule_id:
            return f"/jobs?scheduleId={schedule_id}"

        device_id = str(item.get("device_id") or "").strip()
        if device_id:
            return f"/devices?deviceId={device_id}"

        agent_id = str(item.get("agent_id") or "").strip()
        if agent_id:
            return f"/agents?agentId={agent_id}"

        return "/overview"

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

    def _parse_timestamp(self, value: str) -> datetime:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(
            timezone.utc
        )

    def _format_timestamp(self, value: datetime) -> str:
        return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        )

    def _calculate_next_run_at(self, schedule: dict[str, Any], scheduled_for: str) -> str | None:
        interval_seconds = schedule.get("interval_seconds")
        if interval_seconds:
            next_time = self._parse_timestamp(scheduled_for) + timedelta(
                seconds=int(interval_seconds)
            )
            return self._format_timestamp(next_time)
        cron_expression = str(schedule.get("cron") or "").strip()
        if cron_expression:
            return self._calculate_cron_next_run_at(
                cron_expression,
                scheduled_for,
                str(schedule.get("timezone") or "UTC").strip() or "UTC",
            )
        return None

    def _calculate_cron_next_run_at(self, expression: str, scheduled_for: str, timezone_name: str) -> str:
        fields = expression.split()
        if len(fields) != 5:
            raise ValueError("invalid_cron_expression")
        minute_field, hour_field, day_field, month_field, weekday_field = fields
        zone = ZoneInfo(timezone_name)
        cursor = self._parse_timestamp(scheduled_for).astimezone(zone).replace(second=0, microsecond=0) + timedelta(minutes=1)
        for _ in range(0, 60 * 24 * 370):
            if (
                self._cron_field_matches(minute_field, cursor.minute, 0, 59)
                and self._cron_field_matches(hour_field, cursor.hour, 0, 23)
                and self._cron_field_matches(day_field, cursor.day, 1, 31)
                and self._cron_field_matches(month_field, cursor.month, 1, 12)
                and self._cron_field_matches(weekday_field, (cursor.weekday() + 1) % 7, 0, 6)
            ):
                return self._format_timestamp(cursor.astimezone(timezone.utc))
            cursor += timedelta(minutes=1)
        raise ValueError("cron_next_run_not_found")

    def _cron_field_matches(self, field: str, value: int, minimum: int, maximum: int) -> bool:
        for part in field.split(","):
            token = part.strip()
            if not token:
                continue
            if token == "*":
                return True
            step = 1
            base = token
            if "/" in token:
                base, step_token = token.split("/", 1)
                step = int(step_token)
            if base == "*":
                if (value - minimum) % step == 0:
                    return True
                continue
            if "-" in base:
                start_token, end_token = base.split("-", 1)
                start = int(start_token)
                end = int(end_token)
                if start <= value <= end and (value - start) % step == 0:
                    return True
                continue
            candidate = int(base)
            if minimum <= candidate <= maximum and value == candidate:
                return True
        return False

    def _create_queued_job_run(
        self,
        schedule: dict[str, Any],
        scheduled_for: str,
        *,
        attempt: int,
        trigger_mode: str,
    ) -> dict[str, Any]:
        schedule_id = str(schedule.get("schedule_id") or "").strip()
        job_run_id = self._build_job_run_id(schedule_id, scheduled_for, attempt=attempt)
        run_record = {
            "job_run_id": job_run_id,
            "schedule_id": schedule_id,
            "job_type": schedule.get("job_type"),
            "executor_type": schedule.get("executor_type"),
            "scheduled_for": scheduled_for,
            "status": "queued",
            "attempt": attempt,
            "trigger_mode": trigger_mode,
            "misfire_policy": schedule.get("misfire_policy", "run_once"),
            "misfire_grace_seconds": int(schedule.get("misfire_grace_seconds", 0) or 0),
            "retry_policy": schedule.get("retry_policy", "never"),
            "max_retry_attempts": int(schedule.get("max_retry_attempts", 0) or 0),
            "retry_backoff_seconds": int(schedule.get("retry_backoff_seconds", 0) or 0),
            "payload": deepcopy(schedule.get("payload") or {}),
        }
        self._write_yaml(self.root_dir / "job_runs" / f"{job_run_id}.yaml", run_record)
        return run_record

    def _create_retry_job_run(self, failed_run: dict[str, Any]) -> dict[str, Any] | None:
        retry_policy = str(failed_run.get("retry_policy") or "never").strip().lower()
        if retry_policy == "never":
            return None
        current_attempt = int(failed_run.get("attempt", 1) or 1)
        max_retry_attempts = int(failed_run.get("max_retry_attempts", 0) or 0)
        if current_attempt > max_retry_attempts:
            return None
        schedule = self.get_schedule(str(failed_run.get("schedule_id") or ""))
        if schedule is None:
            return None
        scheduled_for = self._compute_retry_scheduled_for(failed_run)
        return self._create_queued_job_run(
            schedule,
            scheduled_for,
            attempt=current_attempt + 1,
            trigger_mode="retry",
        )

    def _compute_retry_scheduled_for(self, failed_run: dict[str, Any]) -> str:
        failed_at = str(failed_run.get("failed_at") or failed_run.get("scheduled_for") or "").strip()
        base_time = self._parse_timestamp(failed_at)
        retry_policy = str(failed_run.get("retry_policy") or "never").strip().lower()
        backoff_seconds = int(failed_run.get("retry_backoff_seconds", 0) or 0)
        if retry_policy == "fixed_backoff" and backoff_seconds > 0:
            base_time += timedelta(seconds=backoff_seconds)
        return self._format_timestamp(base_time)

    def _build_job_run_id(self, schedule_id: str, scheduled_for: str, *, attempt: int = 1) -> str:
        clean_timestamp = (
            scheduled_for.replace("-", "")
            .replace(":", "")
            .replace("T", "T")
            .replace("Z", "Z")
        )
        return f"run-{schedule_id}-{clean_timestamp}-a{attempt}"
