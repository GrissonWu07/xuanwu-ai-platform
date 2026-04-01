from __future__ import annotations

from collections.abc import Mapping


def import_control_plane_bundle(store, bundle: Mapping) -> dict[str, int]:
    summary = {"server": 0, "agents": 0, "devices": 0}

    server_payload = bundle.get("server")
    if isinstance(server_payload, Mapping):
        store.save_server_profile(dict(server_payload))
        summary["server"] = 1

    for agent_id, payload in _iter_named_items(bundle.get("agents"), "agent_id"):
        store.save_agent(agent_id, payload)
        summary["agents"] += 1

    for device_id, payload in _iter_named_items(bundle.get("devices"), "device_id"):
        store.save_device(device_id, payload)
        summary["devices"] += 1

    return summary


def _iter_named_items(payload, identity_key: str):
    if isinstance(payload, Mapping):
        for item_id, item_payload in payload.items():
            normalized = dict(item_payload) if isinstance(item_payload, Mapping) else {}
            normalized.setdefault(identity_key, item_id)
            yield item_id, normalized
        return

    if isinstance(payload, list):
        for item_payload in payload:
            if not isinstance(item_payload, Mapping):
                continue
            item_id = str(item_payload.get(identity_key, "")).strip()
            if item_id:
                yield item_id, dict(item_payload)
