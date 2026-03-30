from core.adapters.base import BaseGatewayAdapter


class HomeAssistantAdapter(BaseGatewayAdapter):
    adapter_type = "home_assistant"
    display_name = "Home Assistant Adapter"

