from __future__ import annotations

import json
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

from core.adapters.base import BaseGatewayAdapter
from core.adapters.exceptions import GatewayConfigurationError, GatewayExecutionError
from core.contracts.models import build_command_result


class HttpAdapter(BaseGatewayAdapter):
    adapter_type = "http"
    display_name = "HTTP Adapter"
    supported_capabilities = ("switch.on_off", "actuator.http", "device.command")

    def __init__(self, *, transport=None):
        self.transport = transport or UrlLibHttpTransport()

    def validate_command(self, command: dict) -> None:
        super().validate_command(command)
        route = dict(command.get("route") or {})
        url = str(route.get("url") or "").strip()
        method = str(route.get("method") or "").strip().upper()
        if not url:
            raise GatewayConfigurationError("route_url_required", "route.url is required")
        if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
            raise GatewayConfigurationError("route_method_invalid", "route.method is invalid")

    def execute_command(self, command: dict) -> dict:
        route = dict(command.get("route") or {})
        arguments = dict(command.get("arguments") or {})
        response = self.transport.request(
            method=str(route.get("method") or "POST").strip().upper(),
            url=str(route.get("url") or "").strip(),
            headers=dict(route.get("headers") or {}),
            json_body=_render_template(route.get("body_template"), arguments),
            timeout_ms=int(route.get("timeout_ms") or 5000),
        )
        status_code = int(response.get("status_code") or 0)
        if status_code >= 400:
            raise GatewayExecutionError(
                "http_request_failed",
                "HTTP actuator request failed",
                details={"status_code": status_code, "body": response.get("body")},
            )
        return build_command_result(
            command,
            adapter_type=self.adapter_type,
            status="succeeded",
            result={
                "device_id": command.get("device_id"),
                "capability_code": command.get("capability_code"),
                "command_name": command.get("command_name"),
                "arguments": arguments,
                "protocol_response": response.get("body"),
                "status_code": status_code,
            },
        )


class UrlLibHttpTransport:
    def request(self, *, method, url, headers, json_body, timeout_ms):
        data = None
        request_headers = dict(headers or {})
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            request_headers.setdefault("Content-Type", "application/json")
        req = urllib_request.Request(url=url, data=data, method=method, headers=request_headers)
        try:
            with urllib_request.urlopen(req, timeout=max(timeout_ms / 1000.0, 0.1)) as response:
                body = response.read()
                return {
                    "status_code": response.status,
                    "headers": dict(response.headers.items()),
                    "body": _parse_body(body, response.headers.get("Content-Type", "")),
                }
        except HTTPError as exc:
            body = exc.read() if hasattr(exc, "read") else b""
            return {
                "status_code": exc.code,
                "headers": dict(exc.headers.items()) if exc.headers else {},
                "body": _parse_body(body, exc.headers.get("Content-Type", "") if exc.headers else ""),
            }
        except URLError as exc:
            raise GatewayExecutionError("http_transport_error", "HTTP transport error", details={"reason": str(exc)})


def _render_template(template, arguments: dict):
    if template is None:
        return arguments or None
    if isinstance(template, dict):
        return {key: _render_template(value, arguments) for key, value in template.items()}
    if isinstance(template, list):
        return [_render_template(value, arguments) for value in template]
    if isinstance(template, str) and template.startswith("{arguments.") and template.endswith("}"):
        path = template[len("{arguments.") : -1]
        value = arguments
        for part in path.split("."):
            value = value.get(part) if isinstance(value, dict) else None
        return value
    return template


def _parse_body(body: bytes, content_type: str):
    if not body:
        return None
    if "application/json" in str(content_type).lower():
        return json.loads(body.decode("utf-8"))
    return body.decode("utf-8")

