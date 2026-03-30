import sys
from pathlib import Path

from aiohttp import web

SERVICE_ROOT = Path(__file__).resolve().parent
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))

from core.http_server import create_http_app


def create_app(config: dict) -> web.Application:
    return create_http_app(config)

