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
        payload.setdefault("device_id", device_id)
        self._write_yaml(self.root_dir / "devices" / f"{device_id}.yaml", payload)
        return payload

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        return self._read_yaml(self.root_dir / "agents" / f"{agent_id}.yaml")

    def save_agent(self, agent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(payload)
        payload.setdefault("agent_id", agent_id)
        self._write_yaml(self.root_dir / "agents" / f"{agent_id}.yaml", payload)
        return payload

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
        agent_id = device.get("agent_id") or "default"
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
            "agent": {
                "agent_id": agent_id,
                "prompt": resolved_config.get("prompt"),
                "prompt_template": resolved_config.get("prompt_template"),
                "modules": deepcopy(resolved_config.get("selected_module", {})),
            },
            "resolved_config": resolved_config,
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
