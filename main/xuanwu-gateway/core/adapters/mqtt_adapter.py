from core.adapters.base import BaseGatewayAdapter


class MqttAdapter(BaseGatewayAdapter):
    adapter_type = "mqtt"
    display_name = "MQTT Adapter"

