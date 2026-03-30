from core.adapters.base import BaseGatewayAdapter


class HttpAdapter(BaseGatewayAdapter):
    adapter_type = "http"
    display_name = "HTTP Adapter"

