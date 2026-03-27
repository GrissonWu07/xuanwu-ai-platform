# Java 下线检查清单

## 目标

在不影响 `AtlasClaw -> xiaozhi-server -> device` 主对话链路的前提下，让 `manager-api`、`manager-web`、`manager-mobile` 退出运行依赖。

## 当前状态

- 主对话链路已经切到 `AtlasClaw`。
- `xiaozhi-server` 已具备本地 `control-plane`：
  - `GET/PUT /control-plane/v1/config/server`
  - `GET/PUT /control-plane/v1/devices/{device_id}`
  - `GET/PUT /control-plane/v1/agents/{agent_id}`
  - `POST /control-plane/v1/runtime/device-config:resolve`
- 本地导入脚本已提供：
  - `main/xiaozhi-server/scripts/import_control_plane_bundle.py`

## 下线前必须确认

### 1. 主链路确认

- 设备连接后，`startToChat()` 走 `DialogueEngine`。
- `AtlasClaw` 不可用时，默认使用 Level 1 模板 fallback。
- 本地工具不会在 `xiaozhi-server` 内被“智能决定”，而是只通过 runtime API 被 AtlasClaw 调用。

### 2. 配置源确认

- `config_loader.py` 优先读取本地 `control-plane`。
- `manager-api` 只作为兼容配置源，而不是唯一真源。
- 至少存在一份本地 `control-plane` 数据目录：
  - `data/control_plane/server.yaml`
  - `data/control_plane/agents/*.yaml`
  - `data/control_plane/devices/*.yaml`

### 3. Secret / 鉴权确认

- `resolve_control_secret()` 已经成为统一控制密钥入口。
- `runtime API` 与 `control-plane API` 都不再直接依赖 `manager-api.secret`。
- 如果需要保留旧 Java 控制消息，必须确认 `manager-api.url` 仍然有效。

### 4. 兼容残留确认

这些能力仍属于 Java 兼容层，正式下线前要么迁移，要么显式关闭：

- 聊天历史上报
- `mem_local_short` 的远端 summary 保存
- `server` 类型的旧控制消息

## 建议迁移顺序

1. 从 Java 导出 `server/devices/agents` 数据。
2. 使用 `import_control_plane_bundle.py` 导入本地 control-plane。
3. 启动纯 Python 模式，验证：
   - WebSocket
   - OTA
   - Vision
   - Runtime API
   - Control-plane API
4. 关闭 `manager-web`、`manager-mobile`。
5. 将 `manager-api` 切到只读或直接停用。

## 导入 Bundle 约定

支持 JSON 或 YAML，推荐结构：

```yaml
server:
  server:
    runtime_secret: your-secret
agents:
  - agent_id: default
    prompt: agent prompt
devices:
  esp32-001:
    bind_status: bound
    agent_id: default
```

导入命令示例：

```powershell
python main/xiaozhi-server/scripts/import_control_plane_bundle.py `
  C:\path\to\bundle.yaml `
  --output-dir C:\Projects\githubs\xiaozhi-esp32-server\main\xiaozhi-server\data\control_plane
```

## 验收口径

- 关闭 `manager-api` 后，设备仍可完成最小对话闭环。
- `control-plane/v1/runtime/device-config:resolve` 可以独立给出设备运行时配置。
- `manager-web`、`manager-mobile` 不再参与任何主对话路径。
