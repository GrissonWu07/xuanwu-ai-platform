from __future__ import annotations

from typing import Protocol


class ControlPlaneStore(Protocol):
    def load_server_profile(self) -> dict: ...

    def save_server_profile(self, payload: dict) -> dict: ...
