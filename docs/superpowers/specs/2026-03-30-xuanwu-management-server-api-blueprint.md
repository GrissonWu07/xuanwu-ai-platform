# xuanwu-management-server API 蓝图

## 1. 目的

本文档定义 `xuanwu-management-server` 在平台中的 API 范围、数据职责和实现边界。

它是本项目的控制中心、管理中心和设备治理中心。

## 2. 模块职责

`xuanwu-management-server` 负责：

- 用户管理
- 设备注册、认领、绑定、生命周期管理
- 频道、站点、分组管理
- 用户、设备、频道、Agent 的映射关系管理
- 设备能力目录管理
- 网关配置与协议路由管理
- 事件、遥测、告警、审计统一接入和查询
- OTA 元数据与升级治理
- 对 `XuanWu` 的管理代理

不负责：

- Agent 真源
- Model / Knowledge / Workflow 真源
- Agent 运行时推理与设备调用决策
- 设备南向协议执行

## 3. API 分区

### 3.1 用户与身份

- `POST /control-plane/v1/auth/login`
- `POST /control-plane/v1/auth/logout`
- `GET /control-plane/v1/users`
- `POST /control-plane/v1/users`
- `GET /control-plane/v1/users/{user_id}`
- `PUT /control-plane/v1/users/{user_id}`
- `DELETE /control-plane/v1/users/{user_id}`

### 3.2 设备目录与生命周期

- `GET /control-plane/v1/devices`
- `POST /control-plane/v1/devices`
- `POST /control-plane/v1/devices:batch-import`
- `GET /control-plane/v1/devices/{device_id}`
- `PUT /control-plane/v1/devices/{device_id}`
- `POST /control-plane/v1/devices/{device_id}:claim`
- `POST /control-plane/v1/devices/{device_id}:bind`
- `POST /control-plane/v1/devices/{device_id}:suspend`
- `POST /control-plane/v1/devices/{device_id}:retire`

### 3.3 频道与控制视图

- `GET /control-plane/v1/channels`
- `POST /control-plane/v1/channels`
- `GET /control-plane/v1/channels/{channel_id}`
- `PUT /control-plane/v1/channels/{channel_id}`
- `DELETE /control-plane/v1/channels/{channel_id}`

### 3.4 关系映射

- `GET /control-plane/v1/mappings/user-devices`
- `POST /control-plane/v1/mappings/user-devices`
- `GET /control-plane/v1/mappings/user-channels`
- `POST /control-plane/v1/mappings/user-channels`
- `GET /control-plane/v1/mappings/channel-devices`
- `POST /control-plane/v1/mappings/channel-devices`
- `GET /control-plane/v1/mappings/device-agents`
- `POST /control-plane/v1/mappings/device-agents`
- `GET /control-plane/v1/mappings/agent-model-providers`
- `GET /control-plane/v1/mappings/agent-model-configs`
- `GET /control-plane/v1/mappings/agent-knowledge`
- `GET /control-plane/v1/mappings/agent-workflows`

### 3.5 设备能力与路由

- `GET /control-plane/v1/capabilities`
- `POST /control-plane/v1/capabilities`
- `GET /control-plane/v1/capability-routes`
- `POST /control-plane/v1/capability-routes`
- `GET /control-plane/v1/gateways`
- `POST /control-plane/v1/gateways`
- `GET /control-plane/v1/gateways/{gateway_id}`
- `PUT /control-plane/v1/gateways/{gateway_id}`

### 3.6 遥测、事件、告警

- `POST /control-plane/v1/events`
- `POST /control-plane/v1/telemetry`
- `GET /control-plane/v1/events`
- `GET /control-plane/v1/events/{event_id}`
- `GET /control-plane/v1/telemetry`
- `GET /control-plane/v1/alarms`
- `POST /control-plane/v1/alarms/{alarm_id}:ack`

### 3.7 OTA 治理

- `GET /control-plane/v1/ota/firmwares`
- `POST /control-plane/v1/ota/firmwares`
- `GET /control-plane/v1/ota/firmwares/{firmware_id}`
- `PUT /control-plane/v1/ota/firmwares/{firmware_id}`
- `POST /control-plane/v1/ota/campaigns`
- `GET /control-plane/v1/ota/campaigns`

### 3.8 Runtime 解析

- `POST /control-plane/v1/runtime/device-config:resolve`
- `GET /control-plane/v1/runtime/devices/{device_id}/binding-view`
- `GET /control-plane/v1/runtime/devices/{device_id}/capability-routing-view`

### 3.9 `XuanWu` 代理

- `GET /control-plane/v1/xuanwu/agents`
- `POST /control-plane/v1/xuanwu/agents`
- `GET /control-plane/v1/xuanwu/agents/{agent_id}`
- `PUT /control-plane/v1/xuanwu/agents/{agent_id}`
- `DELETE /control-plane/v1/xuanwu/agents/{agent_id}`
- `GET /control-plane/v1/xuanwu/model-providers`
- `POST /control-plane/v1/xuanwu/model-providers`
- `GET /control-plane/v1/xuanwu/models`
- `POST /control-plane/v1/xuanwu/models`
- 后续补 `knowledge` / `workflow` 代理

## 4. 数据真源边界

本模块是真源：

- 用户
- 设备
- 频道
- 网关
- 设备能力目录
- 能力路由
- 遥测
- 事件
- 告警
- OTA 元数据
- 所有关系映射

本模块不是真源：

- Agent
- Model Provider
- Model Config
- Knowledge
- Workflow

## 5. 聚合视图职责

本模块需要负责形成并暴露：

- `DeviceRuntimeBindingView`
- `DeviceCapabilityRoutingView`
- `UserControlScopeView`
- `GatewayRouteView`

这些视图供：

- `xuanwu-device-server`
- `XuanWu`
- 后续管理前端

统一消费。

## 6. 与其他模块的关系

### 6.1 与 `xuanwu-device-server`

- 提供设备配置解析
- 提供设备绑定视图
- 提供运行覆盖参数
- 提供 OTA 治理元数据

### 6.2 与 `XuanWu`

- 代理管理 API
- 提供设备目录、映射、能力、路由聚合结果
- 接收 `XuanWu` 消费后的事件、执行结果回执需求

### 6.3 与 `xuanwu-gateway`

- 下发网关配置
- 接收网关上报的标准事件、遥测、命令结果
- 维护网关目录和健康状态

## 7. 分阶段实现建议

### 7.1 第一阶段

- 用户
- 设备
- 频道
- 基础映射
- runtime resolve
- `XuanWu` 代理

### 7.2 第二阶段

- 设备能力目录
- 能力路由
- 网关目录
- 遥测 / 事件 / 告警

### 7.3 第三阶段

- OTA campaign
- 审计
- 多租户权限
- 更完整的治理能力

## 8. 结论

`xuanwu-management-server` 是本项目最核心的控制平面。

它需要成为本项目所有非 Agent 域真源、关系映射真源、设备治理真源与统一 API 宿主。
