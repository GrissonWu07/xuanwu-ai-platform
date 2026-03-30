from __future__ import annotations

from core.adapters.home_assistant_adapter import HomeAssistantAdapter
from core.adapters.http_adapter import HttpAdapter
from core.adapters.mqtt_adapter import MqttAdapter


class AdapterRegistry:
    def __init__(self):
        self._adapters: dict[str, object] = {}

    def register(self, adapter):
        self._adapters[adapter.adapter_type] = adapter
        return adapter

    def get(self, adapter_type: str):
        return self._adapters.get(str(adapter_type or "").strip())

    def describe(self) -> list[dict]:
        return [adapter.describe() for _, adapter in sorted(self._adapters.items())]


def create_builtin_registry() -> AdapterRegistry:
    registry = AdapterRegistry()
    registry.register(HttpAdapter())
    registry.register(MqttAdapter())
    registry.register(HomeAssistantAdapter())
    return registry

