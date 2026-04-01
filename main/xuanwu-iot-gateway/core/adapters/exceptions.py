from __future__ import annotations


class GatewayAdapterError(Exception):
    def __init__(self, code: str, message: str, *, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class GatewayConfigurationError(GatewayAdapterError):
    def __init__(self, code: str, message: str, *, details: dict | None = None):
        super().__init__(code, message, status_code=400, details=details)


class GatewayExecutionError(GatewayAdapterError):
    def __init__(self, code: str, message: str, *, details: dict | None = None):
        super().__init__(code, message, status_code=502, details=details)
