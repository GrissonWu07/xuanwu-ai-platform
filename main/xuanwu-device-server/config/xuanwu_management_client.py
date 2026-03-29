from __future__ import annotations

from typing import Any

import httpx
from core.runtime_config_exceptions import DeviceBindException, DeviceNotFoundException


def is_xuanwu_management_server_enabled(config: dict[str, Any]) -> bool:
    management_config = config.get("xuanwu-management-server", {})
    return bool(management_config.get("enabled")) and bool(management_config.get("url"))


def _management_config(config: dict[str, Any]) -> dict[str, Any]:
    management_config = config.get("xuanwu-management-server", {})
    if not management_config:
        raise ValueError("xuanwu-management-server configuration missing")
    if not management_config.get("url"):
        raise ValueError("xuanwu-management-server url missing")
    if not management_config.get("secret"):
        raise ValueError("xuanwu-management-server secret missing")
    return management_config


def _client_kwargs(config: dict[str, Any]) -> dict[str, Any]:
    management_config = _management_config(config)
    return {
        "base_url": str(management_config["url"]).rstrip("/"),
        "timeout": float(management_config.get("timeout", 10)),
        "headers": {
            "X-Xuanwu-Control-Secret": str(management_config["secret"]).strip(),
            "Accept": "application/json",
        },
    }


async def fetch_server_config(config: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(**_client_kwargs(config)) as client:
        response = await client.get("/control-plane/v1/config/server")
        response.raise_for_status()
        return response.json()


async def resolve_private_config(
    config: dict[str, Any],
    device_id: str,
    client_id: str,
    selected_module: dict[str, Any],
) -> dict[str, Any]:
    async with httpx.AsyncClient(**_client_kwargs(config)) as client:
        response = await client.post(
            "/control-plane/v1/runtime/device-config:resolve",
            json={
                "device_id": device_id,
                "client_id": client_id,
                "selected_module": selected_module,
            },
        )
        if response.status_code == 404:
            raise DeviceNotFoundException(device_id)
        if response.status_code == 409:
            payload = response.json()
            raise DeviceBindException(payload.get("bind_code"))
        response.raise_for_status()
        payload = response.json()
        return payload.get("resolved_config", payload)


async def report_chat_history(
    config: dict[str, Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    async with httpx.AsyncClient(**_client_kwargs(config)) as client:
        response = await client.post("/control-plane/v1/chat-history/report", json=payload)
        response.raise_for_status()
        return response.json()


async def generate_chat_summary(
    config: dict[str, Any],
    summary_id: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    async with httpx.AsyncClient(**_client_kwargs(config)) as client:
        response = await client.post(
            f"/control-plane/v1/chat-summaries/{summary_id}:generate",
            json=payload or {},
        )
        response.raise_for_status()
        return response.json()
