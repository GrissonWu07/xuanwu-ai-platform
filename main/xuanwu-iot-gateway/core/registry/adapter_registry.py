from __future__ import annotations

from core.adapters.bacnet_ip_adapter import BacnetIpAdapter
from core.adapters.bluetooth_adapter import BluetoothAdapter
from core.adapters.can_gateway_adapter import CanGatewayAdapter
from core.adapters.sensor_http_push_adapter import SensorHttpPushAdapter
from core.adapters.sensor_mqtt_adapter import SensorMqttAdapter
from core.adapters.home_assistant_adapter import HomeAssistantAdapter
from core.adapters.http_adapter import HttpAdapter
from core.adapters.modbus_tcp_adapter import ModbusTcpAdapter
from core.adapters.mqtt_adapter import MqttAdapter
from core.adapters.nearlink_adapter import NearlinkAdapter
from core.adapters.opc_ua_adapter import OpcUaAdapter


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
    registry.register(SensorHttpPushAdapter())
    registry.register(SensorMqttAdapter())
    registry.register(ModbusTcpAdapter())
    registry.register(OpcUaAdapter())
    registry.register(BacnetIpAdapter())
    registry.register(CanGatewayAdapter())
    registry.register(BluetoothAdapter())
    registry.register(NearlinkAdapter())
    return registry

