# XuanWu Agent 域 API 合同 Spec

## 1. 目的

本文档定义所有应由 `XuanWu` 承担的 Agent 域能力，以及本项目与 `XuanWu` 的 API 合同边界。

核心原则：

- 所有需要 `Agent` 认知、编排、决策、设备调用的功能都属于 `XuanWu`
- 本项目不再维护第二套 Agent 真源
- 本项目只基于 `XuanWu` API 规范做设计、透传、映射和运行时集成

## 2. 责任边界

### 2.1 `XuanWu` 负责

必须由 `XuanWu` 承担的能力包括：

- `Agent` 真源
- `Model Provider` 真源
- `Model Config` 真源
- `Knowledge` 真源
- `Workflow` 真源
- `Prompt` / `Template` / `Feature` 等智能体域资源真源
- Agent 运行时编排
- Agent 对设备标准能力的实际调用决策
- Agent 运行时上下文、策略、推理和工具编排

### 2.2 `ai-assist-device` 不负责

本项目不再承担：

- 第二套 `Agent` 数据真源
- 第二套 `Model Provider / Model Config` 真源
- 第二套 `Knowledge / Workflow` 真源
- Agent 自主推理逻辑
- Agent 调用设备的业务决策逻辑

### 2.3 `ai-assist-device` 负责

本项目仍然负责：

- 设备注册、生命周期、设备目录
- 用户、设备、频道、Agent 的关系映射
- 标准能力目录
- 网关配置、能力路由
- 遥测、事件、告警、审计
- 对 `XuanWu` 的管理代理
- 会话型设备接入与运行时执行

## 3. 核心集成原则

### 3.1 单一真源

Agent 域对象全部以 `XuanWu` 为唯一真源：

- `Agent`
- `Model Provider`
- `Model Config`
- `Knowledge`
- `Workflow`
- 后续的 Prompt / Template / Feature / MCP 等 Agent 域对象

### 3.2 管理面代理

`xuanwu-management-server` 对外提供管理入口，但这些对象的数据读写全部代理到 `XuanWu`。

### 3.3 设备调用链

设备调用标准链路是：

1. `xuanwu-management-server` 维护设备、映射、能力、网关路由
2. `XuanWu` 读取聚合后的运行绑定结果
3. `XuanWu` 发起标准能力调用
4. `xuanwu-iot-gateway` 执行南向协议调用
5. 执行结果和事件回流到 `xuanwu-management-server`

## 4. `XuanWu` 必须提供的 API 域

### 4.1 Admin 管理 API

#### 4.1.1 Agent

- `GET /xuanwu/v1/admin/agents`
- `POST /xuanwu/v1/admin/agents`
- `GET /xuanwu/v1/admin/agents/{agent_id}`
- `PUT /xuanwu/v1/admin/agents/{agent_id}`
- `DELETE /xuanwu/v1/admin/agents/{agent_id}`

#### 4.1.2 Model Provider

- `GET /xuanwu/v1/admin/model-providers`
- `POST /xuanwu/v1/admin/model-providers`
- `GET /xuanwu/v1/admin/model-providers/{provider_id}`
- `PUT /xuanwu/v1/admin/model-providers/{provider_id}`
- `DELETE /xuanwu/v1/admin/model-providers/{provider_id}`

#### 4.1.3 Model Config

- `GET /xuanwu/v1/admin/models`
- `POST /xuanwu/v1/admin/models`
- `GET /xuanwu/v1/admin/models/{model_id}`
- `PUT /xuanwu/v1/admin/models/{model_id}`
- `DELETE /xuanwu/v1/admin/models/{model_id}`

#### 4.1.4 Knowledge

- `GET /xuanwu/v1/admin/knowledge-bases`
- `POST /xuanwu/v1/admin/knowledge-bases`
- `GET /xuanwu/v1/admin/knowledge-bases/{knowledge_id}`
- `PUT /xuanwu/v1/admin/knowledge-bases/{knowledge_id}`
- `DELETE /xuanwu/v1/admin/knowledge-bases/{knowledge_id}`

#### 4.1.5 Workflow

- `GET /xuanwu/v1/admin/workflows`
- `POST /xuanwu/v1/admin/workflows`
- `GET /xuanwu/v1/admin/workflows/{workflow_id}`
- `PUT /xuanwu/v1/admin/workflows/{workflow_id}`
- `DELETE /xuanwu/v1/admin/workflows/{workflow_id}`

### 4.2 Runtime 聚合 API

这些接口不是为了后台 CRUD，而是为了本项目获得运行期绑定结果和 Agent 运行期视图。

#### 4.2.1 Agent Runtime Resolve

- `POST /xuanwu/v1/runtime/agents/{agent_id}:resolve`

用途：

- 返回 Agent 运行时编译结果
- 返回模型绑定、知识绑定、工作流绑定
- 返回可执行能力策略和运行标志

#### 4.2.2 Device Command Planning

- `POST /xuanwu/v1/runtime/device-commands:plan`

用途：

- 输入标准能力调用意图
- 输出应调用的设备、能力、参数和执行计划

#### 4.2.3 Device Command Execution

- `POST /xuanwu/v1/runtime/device-commands:execute`

用途：

- 由 `XuanWu` 对具体设备能力调用形成标准命令
- 由本项目进一步路由到 `xuanwu-iot-gateway`

#### 4.2.4 Event / Telemetry Consume

- `POST /xuanwu/v1/runtime/events:ingest`
- `POST /xuanwu/v1/runtime/telemetry:ingest`

用途：

- `XuanWu` 消费经过标准化的事件和遥测
- 用于 Agent 决策、记忆、规则、工作流触发

## 5. 服务间鉴权与协议

### 5.1 请求头

`xuanwu-management-server -> XuanWu` 必须支持：

- `X-Xuanwu-Control-Plane-Secret`
- `X-Request-Id`
- `X-Trace-Id`

### 5.2 错误码

统一约束：

- `200` / `201` 成功
- `400` 参数错误
- `401` 鉴权失败
- `404` 资源不存在
- `409` 资源冲突 / 引用冲突
- `422` 业务校验失败
- `500` 内部错误

### 5.3 响应格式

建议统一：

```json
{
  "ok": true,
  "data": {}
}
```

错误：

```json
{
  "ok": false,
  "error": {
    "code": "resource_conflict",
    "message": "Agent is still bound to active devices",
    "details": {}
  }
}
```

## 6. `XuanWu` 输出给本项目的最小运行视图

### 6.1 AgentRuntimeView

至少应包含：

- `agent_id`
- `status`
- `model_provider_id`
- `model_config_id`
- `knowledge_ids`
- `workflow_ids`
- `execution_policy`
- `device_command_policy`
- `feature_flags`

### 6.2 DeviceCommandPlan

至少应包含：

- `command_id`
- `trace_id`
- `agent_id`
- `target_device_id`
- `capability_code`
- `action_name`
- `arguments`
- `priority`
- `timeout_ms`

## 7. 本项目侧对应实现要求

### 7.1 `xuanwu-management-server`

需要：

- 透传所有 `XuanWu` 管理 API
- 缓存最小化，只做短生命周期代理缓存
- 不落 Agent 域真源
- 维护设备与 Agent 域资源的关系映射
- 为运行期提供聚合视图

### 7.2 `xuanwu-device-gateway`

需要：

- 不再直接拥有 Agent 域配置真源
- 只消费 `xuanwu-management-server` 的运行时配置结果
- 把会话和设备执行链与 `XuanWu` 运行时调用解耦

### 7.3 `xuanwu-iot-gateway`

需要：

- 接收来自 `XuanWu` 规划后的标准能力命令
- 转换为具体设备协议调用
- 回传标准执行结果、标准事件、标准遥测

## 8. 分阶段落地顺序

### 8.1 第一阶段

- `Agent`
- `Model Provider`
- `Model Config`

### 8.2 第二阶段

- `Knowledge`
- `Workflow`

### 8.3 第三阶段

- `Template`
- `Feature`
- `Prompt`
- 后续 MCP / 工具编排管理面

## 9. 结论

凡是需要 `Agent` 认知、编排、运行决策、设备能力调用的功能，都应统一进入 `XuanWu` 需求和实现范围。

本项目必须以 `XuanWu` API 契约为边界，围绕设备、用户、关系、事件、遥测、网关与会话接入进行设计和分步实现。
