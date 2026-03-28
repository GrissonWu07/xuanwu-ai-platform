import asyncio
import json
from typing import Dict, Any

from config.config_loader import is_manager_api_enabled, resolve_control_secret
from core.handle.textMessageHandler import TextMessageHandler
from core.handle.textMessageType import TextMessageType
from core.providers.tools.device_mcp import handle_mcp_message

TAG = __name__

class ServerTextMessageHandler(TextMessageHandler):
    """MCP消息处理器"""

    @property
    def message_type(self) -> TextMessageType:
        return TextMessageType.SERVER

    async def handle(self, conn, msg_json: Dict[str, Any]) -> None:
        # Java 管理 API 的兼容控制消息；本地 control-plane 不走这条路径
        if not is_manager_api_enabled(conn.config):
            return
        post_secret = msg_json.get("content", {}).get("secret", "")
        secret = resolve_control_secret(conn.config)
        if post_secret != secret:
            await conn.websocket.send(
                json.dumps(
                    {
                        "type": "server",
                        "status": "error",
                        "message": "服务器密钥验证失败",
                    }
                )
            )
            return
        # 动态更新配置
        if msg_json["action"] == "update_config":
            try:
                # 更新WebSocketServer的配置
                if not conn.server:
                    await conn.websocket.send(
                        json.dumps(
                            {
                                "type": "server",
                                "status": "error",
                                "message": "无法获取服务器实例",
                                "content": {"action": "update_config"},
                            }
                        )
                    )
                    return

                if not await conn.server.update_config():
                    await conn.websocket.send(
                        json.dumps(
                            {
                                "type": "server",
                                "status": "error",
                                "message": "更新服务器配置失败",
                                "content": {"action": "update_config"},
                            }
                        )
                    )
                    return

                # 发送成功响应
                await conn.websocket.send(
                    json.dumps(
                        {
                            "type": "server",
                            "status": "success",
                            "message": "配置更新成功",
                            "content": {"action": "update_config"},
                        }
                    )
                )
            except Exception as e:
                conn.logger.bind(tag=TAG).error(f"更新配置失败: {str(e)}")
                await conn.websocket.send(
                    json.dumps(
                        {
                            "type": "server",
                            "status": "error",
                            "message": f"更新配置失败: {str(e)}",
                            "content": {"action": "update_config"},
                        }
                    )
                )
        # 重启服务器
        elif msg_json["action"] == "restart":
            await conn.handle_restart(msg_json)
