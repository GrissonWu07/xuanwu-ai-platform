# xiaozhi-runtime Provider 设计

## 1. 目的

本文档定义 `AtlasClaw` 侧的 `xiaozhi-runtime` provider 设计。

该 provider 是 `AtlasClaw` 与 `xiaozhi-server` 之间的能力桥，负责把 Agent 的工具调用转成对 `xiaozhi-server runtime API` 的远程调用。

## 2. 核心原则

- `AtlasClaw` 负责智能决定
- `xiaozhi-server` 负责本地执行
- 所有设备本地高权限动作都通过 provider 调用，不允许进程内直连
- provider 是唯一允许直接访问 `/runtime/v1/*` 的 AtlasClaw 模块

## 3. provider 定位

在 `AtlasClaw` 中，`xiaozhi-runtime` 应属于“设备运行时 provider”。

它不承担：

- session 管理
- 主对话生成
- 长程记忆
- 模型能力

它只承担：

- 获取设备运行时上下文
- 触发设备本地动作
- 执行本地工具
- 打断当前设备播报

## 4. 目录与组织建议

建议放在 provider 目录中：

- `providers/xiaozhi-runtime-provider/`

建议内容：

- `provider.json` 或等价配置
- `client.py`
- `tools/`
- `skills/`

若短期先内置，也至少应保持同样的逻辑结构。

## 5. 配置模型

```json
{
  "base_url": "http://127.0.0.1:8003",
  "runtime_secret": "${XIAOZHI_RUNTIME_SECRET}",
  "timeout_seconds": 15
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `base_url` | string | 是 | `xiaozhi-server` runtime API 地址 |
| `runtime_secret` | string | 是 | 服务间认证密钥 |
| `timeout_seconds` | int | 否 | 超时时间 |

## 6. client 设计

建议新增 `XiaozhiRuntimeClient`：

```python
class XiaozhiRuntimeClient:
    async def get_context(self, runtime_session_id: str) -> dict: ...
    async def execute_tool(self, runtime_session_id: str, name: str, arguments: dict, request_id: str | None = None) -> dict: ...
    async def interrupt(self, runtime_session_id: str, reason: str) -> dict: ...
    async def speak(self, runtime_session_id: str, text: str, interrupt_current: bool = False) -> dict: ...
```

## 7. provider tools 设计

第一批工具必须覆盖当前设备本地能力入口。

### 7.1 `xiaozhi_get_runtime_context`

用途：

- 获取设备能力、状态、session 信息

输入：

- `runtime_session_id` 可选

默认从 `deps.extra["context"]["runtime_session_id"]` 读取

### 7.2 `xiaozhi_execute_local_tool`

用途：

- 执行任意本地工具

输入：

```json
{
  "name": "self_camera_take_photo",
  "arguments": {
    "question": "描述当前画面"
  }
}
```

### 7.3 `xiaozhi_speak_text`

用途：

- 在需要即时反馈时播报短文本

### 7.4 `xiaozhi_interrupt`

用途：

- 中断当前设备播报或设备动作

### 7.5 专用工具封装

在 `xiaozhi_execute_local_tool` 之外，建议提供更友好的专用工具：

- `xiaozhi_take_photo`
- `xiaozhi_call_iot`
- `xiaozhi_call_mcp_tool`

这些工具内部仍统一走 `/tool-executions`。

## 8. Skill 与 Tool 的边界

### 8.1 Tool

负责最小粒度动作：

- 调 runtime API
- 参数校验
- 返回结构化结果

### 8.2 Skill

负责业务编排：

- 何时需要拍照
- 何时先播报再执行
- 何时重试
- 何时向用户解释失败

## 9. 请求上下文约定

所有 `xiaozhi-runtime` tools 默认从 `ctx.deps.extra["context"]` 中读取：

- `runtime_session_id`
- `device_id`
- `client_id`
- `capabilities`

若调用参数显式传入 `runtime_session_id`，则显式参数优先。

## 10. 失败处理

### 10.1 设备断开

- `/runtime/v1/*` 返回 `410`
- provider 转换为结构化错误
- 不自动无限重试

### 10.2 工具不存在

- 返回可读错误
- 由 Agent 决定是否改用其他工具

### 10.3 权限不足

- provider 直接返回错误，不自行绕过

## 11. 与当前本地工具系统的关系

当前 `xiaozhi-server` 的 `UnifiedToolHandler` 继续保留，但角色变更为：

- `xiaozhi-runtime provider` 背后的本地执行器

而不是：

- 由本地 `LLM/Intent` 主动驱动的工具中心

这意味着：

- 智能决定权转移到 `AtlasClaw`
- 执行权保留在 `xiaozhi-server`

## 12. 交付标准

provider 设计完成的标准是：

- 能基于 `runtime_session_id` 定位当前设备
- 能通过统一 client 调用 runtime API
- 能将设备动作暴露为 `AtlasClaw` 标准工具
- 与主对话引擎解耦，不直接依赖 `xiaozhi-server` 内部类
