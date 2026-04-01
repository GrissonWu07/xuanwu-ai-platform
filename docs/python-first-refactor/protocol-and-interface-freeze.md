# 协议与接口冻结设计

## 1. 目的

本文档冻结 `xuanwu-server` 与 `AtlasClaw` 之间的核心协议，作为后续所有实现的基础。

本阶段只做接口与契约设计，不涉及代码实现。

冻结范围：

- `session_key`
- `AgentRunRequest.context`
- `runtime API`
- SSE 事件映射
- 错误码与鉴权约定

## 2. 核心原则

- 协议一旦冻结，后续实现不得在开发中临时扩字段或改语义
- `AtlasClaw` 只通过 HTTP/SSE 和 `xuanwu-server` 交互
- `xuanwu-server` 不暴露内部对象给 `AtlasClaw`
- `AtlasClaw` 的主输入是文本与设备上下文，不是原始音频

## 3. session_key 规范

### 3.1 设计目标

- 保持对 `AtlasClaw session/context.py` 的兼容
- 确保设备是主会话主体
- 支持单设备多连接隔离
- 可稳定恢复上下文

### 3.2 格式

主格式：

`agent:main:user:device-{device_id}:xuanwu:dm:{device_id}`

多连接隔离格式：

`agent:main:user:device-{device_id}:xuanwu:dm:{device_id}:topic:{client_id}`

### 3.3 字段含义

| 段位 | 值 | 含义 |
|---|---|---|
| `agent` | 固定 | AtlasClaw 会话前缀 |
| `main` | 固定 | 主代理 ID |
| `user:device-{device_id}` | 派生 | 将设备映射为会话主体 |
| `xuanwu` | 固定 | 来源 channel |
| `dm` | 固定 | 会话类型 |
| `{device_id}` | 动态 | 设备 peer_id |
| `topic:{client_id}` | 可选 | 并发连接隔离 |

### 3.4 生成规则

- `device_id` 必填
- `client_id` 可选
- 若单设备同时只允许一个对话连接，则不带 `topic`
- 若允许多连接，则必须带 `topic:{client_id}`
- `xuanwu-server` 是唯一允许生成 `session_key` 的组件

## 4. AgentRunRequest.context 冻结

### 4.1 请求结构

`POST /agent/run`

请求体：

```json
{
  "session_key": "agent:main:user:device-esp32-001:xuanwu:dm:esp32-001",
  "message": "帮我查一下今天上海天气",
  "timeout_seconds": 120,
  "context": {
    "device_id": "esp32-001",
    "client_id": "client-001",
    "runtime_session_id": "rt-001",
    "channel": "xuanwu",
    "bind_status": "bound",
    "locale": "zh-CN",
    "audio_format": "opus",
    "capabilities": {
      "speaker": true,
      "camera": true,
      "mcp": true,
      "iot": true
    },
    "device_metadata": {
      "firmware_version": "1.0.0",
      "sample_rate": 24000
    }
  }
}
```

### 4.2 字段定义

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `device_id` | string | 是 | 设备主标识 |
| `client_id` | string | 否 | 当前连接实例 ID |
| `runtime_session_id` | string | 是 | 本地运行时会话 ID |
| `channel` | string | 是 | 固定 `xuanwu` |
| `bind_status` | string | 是 | `bound` / `pending` / `unknown` |
| `locale` | string | 否 | 语言偏好 |
| `audio_format` | string | 否 | 设备音频编码 |
| `capabilities` | object | 是 | 本地能力声明 |
| `device_metadata` | object | 否 | 型号、固件、采样率等 |

### 4.3 `capabilities` 子结构

最小字段：

```json
{
  "speaker": true,
  "camera": false,
  "mcp": true,
  "iot": false
}
```

允许扩展，但禁止删除已冻结字段。

## 5. runtime API 冻结

统一前缀：

- `/runtime/v1`

### 5.1 获取运行时上下文

`GET /runtime/v1/sessions/{runtime_session_id}/context`

成功响应：

```json
{
  "runtime_session_id": "rt-001",
  "device_id": "esp32-001",
  "client_id": "client-001",
  "atlas_session_key": "agent:main:user:device-esp32-001:xuanwu:dm:esp32-001",
  "connected": true,
  "capabilities": {
    "speaker": true,
    "camera": true,
    "mcp": true,
    "iot": true
  },
  "state": {
    "is_speaking": false,
    "listen_mode": "auto",
    "bind_status": "bound"
  }
}
```

### 5.2 执行运行时工具

`POST /runtime/v1/sessions/{runtime_session_id}/tool-executions`

请求：

```json
{
  "request_id": "tool-001",
  "name": "self_camera_take_photo",
  "arguments": {
    "question": "描述当前画面"
  }
}
```

响应：

```json
{
  "status": "ok",
  "request_id": "tool-001",
  "result": {
    "text": "我看到了桌面和一只白色杯子",
    "data": {}
  }
}
```

### 5.3 运行时打断

`POST /runtime/v1/sessions/{runtime_session_id}/interrupt`

请求：

```json
{
  "reason": "new_user_turn"
}
```

响应：

```json
{
  "status": "ok",
  "interrupted": true
}
```

### 5.4 运行时播报

`POST /runtime/v1/sessions/{runtime_session_id}/speak`

请求：

```json
{
  "text": "正在为你处理，请稍等",
  "interrupt_current": false
}
```

响应：

```json
{
  "status": "ok"
}
```

## 6. 运行时鉴权冻结

- Header: `X-Xuanwu-Runtime-Secret`
- 所有 `/runtime/v1/*` 接口均强制校验
- `AtlasClaw` 与 `xuanwu-server` 使用服务间固定密钥
- 不复用设备 token

## 7. SSE 事件映射冻结

`AtlasClaw` SSE 保留原语义：

- `lifecycle`
- `assistant`
- `tool`
- `thinking`
- `error`

本地处理约定：

- `assistant`：进入 TTS 缓冲器
- `tool`：只用于状态/日志，不直接播报
- `thinking`：不播报，默认只记录内部状态
- `error`：触发错误回复策略
- `lifecycle:end`：冲刷剩余 TTS 文本并结束本轮

## 8. 错误码约定

runtime API 统一错误码：

| HTTP 状态码 | 场景 |
|---|---|
| `400` | 请求字段非法 |
| `401` | runtime secret 无效 |
| `404` | runtime session 不存在 |
| `409` | 当前设备状态不允许执行该操作 |
| `410` | 设备已断线 |
| `500` | 本地执行异常 |

## 9. 冻结结论

协议冻结后，后续实现必须遵守以下边界：

- 本地工具不由 `xuanwu-server` 自主智能决定
- 本地工具只能由 `AtlasClaw` 通过 runtime API 调用
- `manager-web`、`manager-api` 不参与主对话链路


