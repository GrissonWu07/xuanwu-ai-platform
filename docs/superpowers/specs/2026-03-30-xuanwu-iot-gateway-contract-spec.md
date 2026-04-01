# xuanwu-iot-gateway 合同规范 Spec

## 1. 目的

本文档定义独立模块 `xuanwu-iot-gateway` 的统一合同。

目标：

- 让 `XuanWu` 能用统一接口调用不同协议、不同类型、不同厂商的设备
- 让 `xuanwu-management-server` 能统一管理网关、设备路由、事件与遥测
- 让所有网关实现共享同一套命令模型、事件模型、错误模型和目录规范

## 2. 角色边界

### 2.1 `xuanwu-management-server`

负责：

- 设备注册与管理
- 用户、频道、设备、Agent 等映射关系
- 网关配置真源
- 设备能力定义真源
- 事件与遥测统一管理

不负责：

- 实际执行设备协议调用

### 2.2 `XuanWu`

负责：

- Agent 推理
- 判断是否调用设备
- 选择调用哪个设备能力
- 调用 `xuanwu-iot-gateway`

不负责：

- 协议细节
- 设备注册真源

### 2.3 `xuanwu-iot-gateway`

负责：

- 协议转换
- 动作执行
- 状态读取
- 遥测与事件标准化
- 执行结果回传

不负责：

- Agent 决策
- 设备目录真源
- 用户关系真源

## 3. 统一调用链

标准调用链固定如下：

1. `xuanwu-management-server` 维护设备、能力、路由、关系映射
2. `XuanWu` 获取聚合视图
3. `XuanWu` 决定调用哪个设备能力
4. `XuanWu` 调用 `xuanwu-iot-gateway`
5. `xuanwu-iot-gateway` 根据网关路由和协议适配器执行动作
6. `xuanwu-iot-gateway` 返回统一执行结果
7. `xuanwu-iot-gateway` 把事件、状态、遥测回流到 `xuanwu-management-server`

## 4. 统一对象

### 4.1 GatewayDefinition

```yaml
gateway_id: mqtt-sensor-01
gateway_type: mqtt
site_id: site-shanghai-01
enabled: true
status: online
connection:
  broker: mqtt://192.168.0.20:1883
auth:
  type: username_password
```

### 4.2 GatewayRoute

```yaml
route_id: route-001
device_id: dev-001
gateway_id: mqtt-sensor-01
protocol_type: mqtt
adapter_type: telemetry_ingest
mapping_profile: default-temperature-sensor
enabled: true
```

### 4.3 CapabilityCommand

```yaml
command_id: cmd-001
trace_id: trace-001
device_id: dev-010
capability_code: switch.on_off
action: turn_on
arguments: {}
timeout_ms: 5000
requested_by: agent/receptionist-agent
```

### 4.4 CapabilityCommandResult

```yaml
command_id: cmd-001
trace_id: trace-001
device_id: dev-010
status: succeeded
gateway_id: mqtt-actuator-01
finished_at: 2026-03-30T12:00:00Z
result:
  acknowledged: true
error: null
```

### 4.5 StandardEvent

```yaml
event_id: evt-001
trace_id: trace-002
device_id: dev-020
gateway_id: mqtt-sensor-01
event_type: telemetry.reported
timestamp: 2026-03-30T12:01:00Z
payload:
  temperature: 24.8
  humidity: 51.2
```

## 5. 统一 API 合同

### 5.1 `XuanWu -> xuanwu-iot-gateway`

建议固定前缀：

- `/gateway/v1`

#### 执行动作

- `POST /gateway/v1/commands`

请求体：

```json
{
  "command_id": "cmd-001",
  "trace_id": "trace-001",
  "device_id": "dev-010",
  "capability_code": "switch.on_off",
  "action": "turn_on",
  "arguments": {},
  "timeout_ms": 5000,
  "requested_by": "agent/receptionist-agent"
}
```

成功响应：

```json
{
  "ok": true,
  "data": {
    "command_id": "cmd-001",
    "trace_id": "trace-001",
    "device_id": "dev-010",
    "status": "succeeded",
    "gateway_id": "mqtt-actuator-01",
    "finished_at": "2026-03-30T12:00:00Z",
    "result": {
      "acknowledged": true
    },
    "error": null
  }
}
```

#### 查询设备实时状态

- `GET /gateway/v1/devices/{device_id}/state`

成功响应：

```json
{
  "ok": true,
  "data": {
    "device_id": "dev-010",
    "gateway_id": "mqtt-actuator-01",
    "state": {
      "power_state": "on",
      "brightness": 80
    },
    "reported_at": "2026-03-30T12:03:00Z"
  }
}
```

### 5.2 `xuanwu-iot-gateway -> xuanwu-management-server`

#### 上报统一事件

- `POST /control-plane/v1/gateway/events`

请求体：

```json
{
  "event_id": "evt-001",
  "trace_id": "trace-002",
  "device_id": "dev-020",
  "gateway_id": "mqtt-sensor-01",
  "event_type": "telemetry.reported",
  "timestamp": "2026-03-30T12:01:00Z",
  "payload": {
    "temperature": 24.8,
    "humidity": 51.2
  }
}
```

#### 上报命令回执

- `POST /control-plane/v1/gateway/command-results`

请求体：

```json
{
  "command_id": "cmd-001",
  "trace_id": "trace-001",
  "device_id": "dev-010",
  "gateway_id": "mqtt-actuator-01",
  "status": "succeeded",
  "finished_at": "2026-03-30T12:00:00Z",
  "result": {
    "acknowledged": true
  },
  "error": null
}
```

### 5.3 `xuanwu-management-server -> xuanwu-iot-gateway`

#### 下发网关配置

- `GET /gateway/v1/config`

响应体：

```json
{
  "ok": true,
  "data": {
    "gateways": [],
    "routes": [],
    "capabilities": []
  }
}
```

#### 健康检查

- `GET /gateway/v1/health`

响应体：

```json
{
  "ok": true,
  "data": {
    "status": "healthy",
    "gateway_node_id": "gateway-node-01"
  }
}
```

## 6. 鉴权规范

### 6.1 `XuanWu -> xuanwu-iot-gateway`

固定请求头：

- `X-xuanwu-iot-gateway-Secret`
- `X-Request-Id`
- `X-Trace-Id`

### 6.2 `xuanwu-iot-gateway -> xuanwu-management-server`

固定请求头：

- `X-Xuanwu-Control-Secret`
- `X-Request-Id`
- `X-Trace-Id`

## 7. 统一状态与错误模型

### 7.1 命令状态

固定枚举：

- `accepted`
- `queued`
- `running`
- `succeeded`
- `failed`
- `timeout`
- `rejected`

### 7.2 错误码

固定错误码建议：

- `device_not_found`
- `gateway_not_found`
- `route_not_found`
- `capability_not_supported`
- `command_rejected`
- `device_offline`
- `protocol_error`
- `gateway_timeout`
- `auth_failed`
- `invalid_payload`
- `internal_error`

### 7.3 HTTP 状态码

- `200` 成功
- `202` 已接收异步执行
- `400` 参数错误
- `401` 鉴权失败
- `404` 设备/网关/路由不存在
- `409` 状态冲突
- `422` 能力或业务校验失败
- `500` 内部错误
- `504` 网关超时

## 8. 分布式要求

`xuanwu-iot-gateway` 必须支持分布式部署。

要求：

- 可多实例部署
- 可按协议类型拆分实例
- 可按站点拆分实例
- 可按区域拆分实例
- 必须支持全局唯一 `gateway_id`
- 必须支持全局唯一 `trace_id`
- 事件与命令结果必须幂等上报

## 9. 目录规范

`xuanwu-iot-gateway` 必须按设备类型和协议分目录组织。

目标目录：

```text
main/
  xuanwu-iot-gateway/
    core/
      contracts/
      models/
      errors/
      auth/
      routing/
      telemetry/
      commands/
    gateways/
      conversation/
        websocket/
        mqtt_gateway/
      actuator/
        http/
        mqtt/
        home_assistant/
      sensor/
        mqtt/
        http_push/
      industrial/
        modbus_tcp/
        opc_ua/
        bacnet_ip/
        can_gateway/
    profiles/
      conversation/
      actuator/
      sensor/
      industrial/
```

约束：

- 每种协议实现独立目录
- 每种设备类型独立目录
- 每种协议适配器都必须实现同一套合同接口

## 10. 协议适配器接口

每个协议适配器至少实现以下语义接口：

- `connect()`
- `disconnect()`
- `health_check()`
- `execute_command(command)`
- `read_state(device_id)`
- `normalize_event(raw_event)`
- `normalize_command_result(raw_result)`

说明：

- 这里是语义接口，不限制具体语言实现
- 但所有适配器都必须产出统一事件模型和统一动作回执模型

## 11. 非目标

本 Spec 当前不展开：

- 单个工业协议的字段级驱动实现
- 数据库存储结构
- 前端页面

## 12. 最终结论

`xuanwu-iot-gateway` 必须成为独立的协议与能力适配平台。

它的核心意义不是“多接几个协议”，而是：

- 为 `XuanWu` 提供统一设备调用合同
- 为 `xuanwu-management-server` 提供统一事件与遥测回流合同
- 为整个平台提供统一的南向适配边界

没有这层，就很难真正演进成完整的通用 IoT 平台。
