import asyncio
import signal
import sys
import uuid

from aioconsole import ainput

from config.config_loader import resolve_control_secret
from config.logger import setup_logging
from config.settings import load_config
from core.http_server import SimpleHttpServer
from core.utils.gc_manager import get_gc_manager
from core.utils.util import (
    check_ffmpeg_installed,
    get_local_ip,
    validate_mcp_endpoint,
)
from core.websocket_server import WebSocketServer

TAG = __name__
logger = setup_logging()


async def wait_for_exit() -> None:
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    if sys.platform != "win32":
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)
        await stop_event.wait()
        return

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        pass


async def monitor_stdin():
    while True:
        await ainput()


async def main():
    check_ffmpeg_installed()
    config = load_config()

    auth_key = config["server"].get("auth_key", "")
    if not auth_key or "浣?" in auth_key:
        auth_key = resolve_control_secret(config)
        if not auth_key or "浣?" in auth_key:
            auth_key = str(uuid.uuid4().hex)
    config["server"]["auth_key"] = auth_key

    stdin_task = asyncio.create_task(monitor_stdin())
    gc_manager = get_gc_manager(interval_seconds=300)
    await gc_manager.start()

    ws_server = WebSocketServer(config)
    ws_task = asyncio.create_task(ws_server.start())
    ota_server = SimpleHttpServer(config)
    ota_task = asyncio.create_task(ota_server.start())

    port = int(config["server"].get("http_port", 8003))
    logger.bind(tag=TAG).info(
        "OTA接口地址是\thttp://{}:{}/xuanwu/ota/",
        get_local_ip(),
        port,
    )
    logger.bind(tag=TAG).info(
        "视觉分析接口是\thttp://{}:{}/mcp/vision/explain",
        get_local_ip(),
        port,
    )

    mcp_endpoint = config.get("mcp_endpoint")
    if mcp_endpoint is not None and "浣?" not in mcp_endpoint:
        if validate_mcp_endpoint(mcp_endpoint):
            logger.bind(tag=TAG).info("mcp接入点是\t{}", mcp_endpoint)
            config["mcp_endpoint"] = mcp_endpoint.replace("/mcp/", "/call/")
        else:
            logger.bind(tag=TAG).error("mcp接入点不符合规范")
            config["mcp_endpoint"] = "你的接入点 websocket 地址"

    websocket_port = int(config.get("server", {}).get("port", 8000))
    logger.bind(tag=TAG).info(
        "Websocket地址是\tws://{}:{}/xuanwu/v1/",
        get_local_ip(),
        websocket_port,
    )
    logger.bind(tag=TAG).info(
        "=======上面的地址是 websocket 协议地址，请勿用浏览器访问======"
    )
    logger.bind(tag=TAG).info(
        "如想测试 websocket，请用谷歌浏览器打开 test 目录下的 test_page.html"
    )
    logger.bind(tag=TAG).info("=============================================================\n")

    try:
        await wait_for_exit()
    except asyncio.CancelledError:
        print("任务被取消，清理资源中...")
    finally:
        await gc_manager.stop()

        stdin_task.cancel()
        ws_task.cancel()
        ota_task.cancel()

        await asyncio.wait(
            [stdin_task, ws_task, ota_task],
            timeout=3.0,
            return_when=asyncio.ALL_COMPLETED,
        )
        print("服务器已关闭，程序退出。")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("手动中断，程序终止。")
