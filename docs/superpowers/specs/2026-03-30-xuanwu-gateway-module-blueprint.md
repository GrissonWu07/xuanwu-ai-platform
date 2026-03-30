# xuanwu-gateway 模块蓝图

## 1. 目的

本文档定义 `xuanwu-gateway` 作为独立协议与能力适配模块的实现蓝图。

## 2. 模块定位

`xuanwu-gateway` 是独立部署、独立扩展、独立维护的南向适配层。

它负责：

- 协议接入
- 厂商设备适配
- 设备状态与事件标准化
- 标准能力命令执行
- 命令结果回传

它不负责：

- Agent 决策
- 设备管理后台
- 用户和设备主目录真源

## 3. 目录组织原则

必须按设备类型与协议分目录，避免全部适配器堆在一起。

推荐结构：

```text
main/xuanwu-gateway/
  app.py
  core/
    contracts/
    runtime/
    registry/
  adapters/
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
  tests/
```

## 4. 模块内部职责分层

### 4.1 contracts

定义统一对象：

- `CapabilityCommand`
- `CapabilityCommandResult`
- `StandardEvent`
- `GatewayDefinition`
- `GatewayRoute`

### 4.2 registry

负责：

- 适配器注册
- 协议到实现的映射
- 能力到执行器的映射

### 4.3 runtime

负责：

- 命令调度
- 执行超时
- 重试策略
- 健康检查
- 回执上报

### 4.4 adapters

负责：

- 协议连接
- 协议读写
- 状态标准化
- 命令映射
- 事件标准化

## 5. 每类设备的接入原则

### 5.1 会话型设备

适配：

- `conversation/websocket`
- `conversation/mqtt_gateway`

说明：

- 会话型设备主要仍由 `xuanwu-device-server` 负责接入
- `xuanwu-gateway` 只承担补充网关适配职责

### 5.2 执行型设备

适配：

- `actuator/http`
- `actuator/mqtt`
- `actuator/home_assistant`

这是 `xuanwu-gateway` 的主战场。

### 5.3 传感器型设备

适配：

- `sensor/mqtt`
- `sensor/http_push`

重点是事件和遥测标准化。

### 5.4 工业设备

适配：

- `industrial/modbus_tcp`
- `industrial/opc_ua`
- `industrial/bacnet_ip`
- `industrial/can_gateway`

重点是工业协议桥接与数据点映射。

## 6. 执行链

标准执行链：

1. `XuanWu` 发起标准能力命令
2. `xuanwu-management-server` 提供目标设备和路由元数据
3. `xuanwu-gateway` 选择匹配适配器
4. 适配器执行协议调用
5. 返回标准命令结果
6. 上报事件、状态、遥测

## 7. 必需 API

### 7.1 北向 API

- `POST /gateway/v1/commands`
- `GET /gateway/v1/devices/{device_id}/state`
- `GET /gateway/v1/health`
- `GET /gateway/v1/config`

### 7.2 南向回流

- `POST /control-plane/v1/gateway/events`
- `POST /control-plane/v1/gateway/telemetry`
- `POST /control-plane/v1/gateway/command-results`

## 8. 分布式要求

必须支持：

- 按协议分片
- 按站点分片
- 按区域分片
- 无状态水平扩展
- 命令与事件的可追踪性

## 9. 实现顺序建议

1. `http`
2. `mqtt`
3. `home_assistant`
4. `modbus_tcp`
5. `opc_ua`
6. `bacnet_ip`
7. `can_gateway`

## 10. 结论

`xuanwu-gateway` 必须独立成为平台的南向协议与能力适配层，而不是散落在各个服务中的临时逻辑集合。
