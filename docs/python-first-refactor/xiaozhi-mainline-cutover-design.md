# xiaozhi-server 主链路切换设计

## 1. 目的

本文档定义如何将 `xiaozhi-server` 的主对话链路从“本地 LLM / Intent / Memory”切换为“AtlasClaw 主对话引擎”。

本次只设计切换方案，不写代码。

## 2. 切换后的主链路

旧链路：

`ASR -> handle_user_intent() -> conn.chat() -> UnifiedToolHandler -> TTS`

新链路：

`ASR -> send_stt_message() -> DialogueEngine.run_turn() -> AtlasClaw -> runtime API -> TTS`

## 3. 保留与移除

### 3.1 保留在本地

- `hello`
- `ping`
- `abort`
- `listen`
- `server`
- OTA
- 音频流控
- VAD / ASR / TTS
- 设备连接生命周期

### 3.2 从主路径移除

- 本地主意图识别
- 本地主回复生成
- 本地主工具规划
- 本地主记忆主导

## 4. `startToChat()` 新职责

当前文件：

- `main/xiaozhi-server/core/handle/receiveAudioHandle.py`

新职责应缩减为：

1. 解析 ASR 文本
2. 校验设备状态
3. 处理中断
4. 发送 STT 消息给设备侧 UI
5. 调用 `conn.dialogue_engine.run_turn(conn, actual_text)`

明确不再做：

- `handle_user_intent(conn, actual_text)`
- `conn.chat(actual_text)`

## 5. 新增 `DialogueEngine`

建议接口：

```python
class DialogueEngine(Protocol):
    async def run_turn(self, conn, user_text: str) -> None: ...
    async def abort_turn(self, conn) -> None: ...
```

实现：

- `AtlasClawDialogueEngine`
- `LocalFallbackDialogueEngine`

## 6. `AtlasClawDialogueEngine` 设计

职责：

- 构造 `session_key`
- 构造 `AgentRunRequest.context`
- 调用 `POST /agent/run`
- 监听 `GET /agent/runs/{run_id}/stream`
- 将 SSE 事件转成 TTS 与状态输出

建议方法：

```python
class AtlasClawDialogueEngine:
    async def run_turn(self, conn, user_text: str) -> None: ...
    async def abort_turn(self, conn) -> None: ...
    async def _start_run(self, conn, user_text: str) -> str: ...
    async def _consume_stream(self, conn, run_id: str) -> None: ...
```

## 7. 连接对象调整

当前 `ConnectionHandler` 过重，但本阶段先不整体拆散，只做能力迁移。

新增字段：

- `runtime_session_id`
- `atlas_session_key`
- `dialogue_engine`
- `atlas_run_id`
- `atlas_stream_task`

移除主用途字段：

- `llm`
- `intent`
- `memory`

这些字段短期可以保留，但只用于 fallback。

## 8. SSE -> TTS 桥接

### 8.1 桥接器职责

新增：

- `AtlasClawStreamBridge`

职责：

- 接收 `assistant` 增量文本
- 做句边界或块边界切分
- 送入现有 TTS 队列
- 在 `lifecycle:end` 时冲刷剩余缓存

### 8.2 事件映射

| SSE 事件 | 本地行为 |
|---|---|
| `assistant` | 缓冲并送入 TTS |
| `thinking:start` | 可选设置内部思考态 |
| `tool:start` | 记录日志 |
| `tool:end` | 更新状态 |
| `error` | 进入错误播报 |
| `lifecycle:end` | 冲刷文本、结束轮次 |

## 9. 中断逻辑

当前用户再次说话时：

1. 本地优先中断当前 TTS
2. 若 `atlas_run_id` 存在，调用 `POST /agent/runs/{run_id}/abort`
3. 清理本地 stream task 状态

这样保证：

- 本地播报立即停
- 远端 Agent 也停止继续生成

## 10. `UnifiedToolHandler` 的主路径变化

重构后：

- `UnifiedToolHandler` 不再由本地 `conn.chat()` 主动驱动
- 它只响应 runtime API 请求

即：

`AtlasClaw tool -> xiaozhi runtime API -> UnifiedToolHandler`

而不是：

`local llm -> UnifiedToolHandler`

## 11. 配置切换

需要新增 `Agent` 配置块：

```yaml
Agent:
  AtlasClaw:
    type: atlasclaw
    base_url: http://127.0.0.1:8000
    timeout_seconds: 120
selected_module:
  Agent: AtlasClaw
```

启动时：

- 必须初始化 `ASR`
- 必须初始化 `TTS`
- 必须初始化 `Agent`
- `LLM / Intent / Memory` 默认不初始化主实例

## 12. 验收标准

- `startToChat()` 不再调用本地主聊天主链路
- 主文本请求全部进入 `AtlasClaw`
- `assistant` 文本能稳定转成 TTS 音频
- 中断能同时中断本地与远端
- 设备控制消息不受影响
