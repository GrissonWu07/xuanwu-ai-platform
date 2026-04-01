# 玄武AI中心化 Agent 物联网平台目标架构 Spec

## 1. 文档目标

本 Spec 定义 `ai-assist-device` 与 `XuanWu` 联合演进后的目标平台形态。

目标平台需要同时满足：

- 尽可能全面地管理智能设备和 IoT 设备
- 具备完整的通用物联网平台能力
- 具备工业化扩展能力
- 通过中心化 Agent 模式统一管理会话型设备
- 通过能力网关统一纳管执行型设备
- 通过事件接入统一纳管传感器型设备

本文档重点回答：

- 每种设备应该如何被建模
- 每种设备支持什么协议类型
- 网关应该如何配置
- `xuanwu-device-gateway`、`xuanwu-management-server`、`XuanWu`、`xuanwu-iot-gateway` 各自负责什么
- 设备注册、设备管理、设备调用、事件与遥测分别归谁负责

## 2. 总体结论

最终平台不应把所有设备都当成“直接运行完整 Agent 的设备”。

正确模型是：

- 会话型设备
  - 是 Agent 终端
  - 负责交互，不负责认知
  - 中央 Agent 在 `XuanWu`
- 执行型 IoT 设备
  - 是能力提供者
  - 通过网关或适配器暴露动作、属性、状态
  - 由中心 Agent 或规则系统调用
- 传感器型设备
  - 是事件和遥测来源
  - 由规则、工作流或中心 Agent 消费其状态和事件

本轮补充后的固定边界是：

- 设备注册与设备管理
  - 全部留在本项目
  - 由 `xuanwu-management-server` 统一承载
- 用户、设备、Agent、Channel、Model/Model Config、Knowledge、Workflow 的关系映射
  - 全部由 `xuanwu-management-server` 维护
  - 不落在设备对象本身
  - 设备默认直接归属到用户
  - 如果没有用户，则归属匿名用户
  - `channel` 是用户名下的控制入口
  - 一个用户可以有多个 `channel`
  - 这些 `channel` 只管理、操作、控制该用户自己的设备
- 设备被 Agent 实际调用
  - 全部放到 `XuanWu`
  - `XuanWu` 负责决定何时调用、调用哪个设备能力、如何编排调用链
- 遥测与事件
  - 统一归 `xuanwu-management-server` 管理
  - 不允许每个接入方式各自维护一套事件口径
- 网关与适配层
  - 作为独立模块实现
  - 固定命名为 `xuanwu-iot-gateway`
  - 不再作为 `xuanwu-management-server` 的临时内嵌逻辑存在

## 3. 目标分层架构

### 3.1 `xuanwu-device-gateway`

职责：

- 会话型设备接入
- WebSocket 实时会话
- 音频流处理
- OTA 执行入口
- 本地执行桥
- 设备运行时状态维护

不负责：

- 管理后台
- 通用设备注册中心
- Agent 真源
- 大规模设备治理

### 3.2 `xuanwu-management-server`

职责：

- 控制面和管理面宿主
- 设备注册、绑定、分组、站点管理
- 设备能力模型与数字孪生
- 网关配置与协议适配管理
- OTA 元数据与升级治理
- 事件与遥测统一接入、统一存储、统一查询
- 权限、审计、策略、审批
- 对 `XuanWu` 的管理代理

这是未来通用 IoT 平台主体。

强约束：

- 所有设备注册与管理都必须通过 `xuanwu-management-server`
- `xuanwu-management-server` 是设备目录、设备生命周期、设备分组、设备能力定义的主真源
- `xuanwu-management-server` 是关系映射真源，负责维护：
  - `user -> device`
  - `user -> channel`
  - `channel -> device`
  - `device -> agent`
  - `agent -> model provider`
  - `agent -> model config`
  - `agent -> knowledge`
  - `agent -> workflow`
- `xuanwu-management-server` 负责把设备元数据、能力定义、网关路由信息暴露给 `XuanWu`
- `xuanwu-management-server` 不负责 Agent 自主决策，也不直接承担 Agent 运行时动作编排

### 3.3 `XuanWu`

职责：

- 中心化 Agent 真源
- Model Provider / Model Config 真源
- 认知编排和推理
- 中心化 Agent 运行时编译
- 后续 Prompt / Workflow / Knowledge 域

新增约束：

- 所有“Agent 实际调用设备”的行为都放在 `XuanWu`
- `XuanWu` 不负责设备注册和设备管理真源
- `XuanWu` 通过能力模型、设备引用、网关引用来调用设备
- `XuanWu` 不能绕过 `xuanwu-management-server` 自建一套设备目录

### 3.4 `xuanwu-iot-gateway`

职责：

- 协议接入
- 命令标准化
- 状态标准化
- 事件标准化
- 外部平台接入
- 工业协议桥接

固定要求：

- `xuanwu-iot-gateway` 是独立模块
- `xuanwu-iot-gateway` 可以独立部署、水平扩展、按协议分片部署
- 所有协议适配器、网关、桥接器都应收敛到 `xuanwu-iot-gateway`
- `xuanwu-management-server` 负责管理 `xuanwu-iot-gateway` 的配置与元数据
- `XuanWu` 负责通过标准能力调用接口使用 `xuanwu-iot-gateway`

### 3.5 分布式要求

目标平台必须支持分布式部署。

最小分布式拓扑：

- `xuanwu-device-gateway`
  - 多实例横向扩展
  - 按会话或接入区域分片
- `xuanwu-management-server`
  - 多实例部署
  - 共享设备目录、配置真源、事件存储
- `XuanWu`
  - 多实例部署
  - 共享 Agent 真源与编排能力
- `xuanwu-iot-gateway`
  - 按协议类型分布式部署
  - 按站点、协议、区域独立扩展

分布式前提：

- 设备 ID 全局唯一
- 网关 ID 全局唯一
- 事件与遥测统一使用标准消息模型
- 所有控制调用必须有 trace_id / request_id

## 4. 设备分类模型

平台统一将设备分为三类：

### 4.1 会话型设备

定义：

- 以语音、文本、多模态交互为主要目标
- 需要会话状态、打断、播报、轮次管理

示例：

- ESP32 语音终端
- 智能音箱
- 语音面板
- AI 对讲机
- 具身交互机器人前端

建模方式：

- `device_type = conversation_terminal`
- `transport = websocket | mqtt-gateway`
- `capabilities = audio_input, audio_output, wakeup, interrupt, optional_vision`

### 4.2 执行型 IoT 设备

定义：

- 以执行动作、接受控制为主
- 不需要完整多轮会话

示例：

- 灯
- 开关
- 窗帘
- 门锁
- 插座
- HVAC 控制器
- 继电器板

建模方式：

- `device_type = actuator`
- `transport = gateway`
- `capabilities = on_off, set_level, set_mode, lock_unlock, open_close, scene_apply`

### 4.3 传感器型设备

定义：

- 以状态采集、事件上报、遥测为主

示例：

- 温湿度传感器
- 人体存在传感器
- 门磁
- 电表
- 水表
- 震动传感器
- 工业遥测设备

建模方式：

- `device_type = sensor`
- `transport = mqtt | http-push | industrial-gateway`
- `capabilities = telemetry, threshold_alarm, state_report, event_report`

## 5. 协议矩阵

本期目标协议范围如下。

### 5.1 会话型设备协议

主协议：

- `WebSocket`
  - 用于实时音频/控制消息
  - 当前主路径
  - 推荐 URL：`ws://host:8000/xuanwu/v1/`
- `MQTT Gateway`
  - 设备侧不直接连运行时，而是通过 MQTT/UDP 网关桥接到 WebSocket
  - 推荐给嵌入式弱设备

补充协议：

- `HTTP OTA`
  - 用于设备引导和固件/连接配置获取
  - 当前主路径：`http://host:8003/xuanwu/ota/`

### 5.2 执行型 IoT 设备协议

推荐协议：

- `HTTP`
  - 适合 REST 风格智能设备或云平台
- `MQTT`
  - 适合轻量级控制设备
- `Home Assistant`
  - 适合作为统一家庭/楼宇设备接入平台

目标扩展协议：

- `Modbus TCP`
- `BACnet/IP`
- `CAN Gateway`

### 5.3 传感器型设备协议

推荐协议：

- `MQTT`
- `HTTP Push`

目标扩展协议：

- `Modbus TCP`
- `OPC UA`
- `BACnet/IP`
- `CAN Gateway`

### 5.4 工业设备目标协议

作为目标适配协议，统一进入“工业网关”层：

- `Modbus TCP`
- `OPC UA`
- `BACnet/IP`
- `CAN Gateway`

说明：

- 本 Spec 将这些协议列为目标能力
- 不代表当前仓库已完整实现
- 后续由独立模块 `xuanwu-iot-gateway` 统一纳管

## 6. 网关架构规范

### 6.1 网关的职责

所有网关必须至少负责：

- 协议接入
- 设备身份映射
- 状态标准化
- 动作标准化
- 事件标准化
- 鉴权
- 错误映射
- 回执或执行结果上报

### 6.2 网关不应该负责

- 独立维护 Agent 逻辑
- 独立实现业务决策
- 独立维护设备主真源
- 绕过 `xuanwu-management-server` 直接成为平台控制中心

### 6.3 网关接入方向

统一方向：

- 南向：设备 / 第三方平台 / 工业总线
- 北向：`xuanwu-management-server`

必要时：

- `xuanwu-management-server` 再把可用能力目录和设备元数据暴露给 `XuanWu`
- `XuanWu` 通过标准设备调用接口实际驱动 `xuanwu-iot-gateway`
- `xuanwu-device-gateway` 只处理会话运行时，不直接成为通用南向网关宿主

### 6.4 网关调用责任链

固定责任链如下：

1. 设备注册、设备能力定义、设备归属、设备分组在 `xuanwu-management-server`
2. `xuanwu-management-server` 把设备引用、能力引用、网关路由暴露给 `XuanWu`
3. `XuanWu` 在 Agent 推理和编排阶段决定是否调用设备
4. `XuanWu` 通过标准接口调用 `xuanwu-iot-gateway`
5. `xuanwu-iot-gateway` 完成协议转换并驱动实际设备
6. 设备状态、执行结果、遥测和事件再统一回流到 `xuanwu-management-server`

## 7. 每类设备的接入与网关策略

### 7.1 会话型设备

#### 接入方式 A：直接 WebSocket

适用：

- ESP32
- 语音终端
- 实时对话设备

配置要点：

- 设备通过 OTA 获取 websocket 地址
- 连接到 `/xuanwu/v1/`
- 带 `device-id`、`client-id`、认证信息
- 运行时配置通过 `xuanwu-management-server` 解析

推荐配置：

```yaml
server:
  websocket: ws://device-runtime.example.com:8000/xuanwu/v1/
  auth:
    enabled: true

xuanwu-management-server:
  enabled: true
  url: http://xuanwu-management-server:18082
  secret: xuanwu-management-local-secret
```

#### 接入方式 B：MQTT Gateway

适用：

- 不适合直接实现完整 WebSocket 协议的嵌入式设备
- 低功耗设备
- 弱网络设备

桥接关系：

- 设备 <-> MQTT/UDP
- 网关 <-> WebSocket Runtime

推荐配置：

```yaml
server:
  mqtt_gateway: 192.168.0.7:1883
  mqtt_signature_key: your-mqtt-signature-key
  udp_gateway: 192.168.0.7:8884
```

网关侧关键配置：

```json
{
  "production": {
    "chat_servers": [
      "ws://127.0.0.1:8000/xuanwu/v1/?from=mqtt_gateway"
    ]
  }
}
```

### 7.2 执行型 IoT 设备

#### 接入方式 A：HTTP 设备网关

适用：

- 提供 HTTP API 的设备
- 云端设备平台
- REST 风格控制器

网关职责：

- 将平台动作映射为 HTTP 请求
- 将结果标准化为统一回执

推荐配置：

```yaml
gateways:
  - gateway_id: http-gateway-01
    type: http
    base_url: http://iot-gateway.local:9000
    auth:
      type: bearer
      token_ref: secret/http_gateway_token
    device_filters:
      - device_type: actuator
```

#### 接入方式 B：MQTT 执行网关

适用：

- 使用 topic 进行控制的 IoT 设备
- 边缘控制器

推荐配置：

```yaml
gateways:
  - gateway_id: mqtt-actuator-01
    type: mqtt
    broker: mqtt://192.168.0.10:1883
    username: gateway-user
    password_ref: secret/mqtt_gateway_password
    command_topic_prefix: devices/cmd/
    state_topic_prefix: devices/state/
```

#### 接入方式 C：Home Assistant 网关

适用：

- 已接入 Home Assistant 的家居设备
- 快速承接异构家庭设备

推荐配置：

```yaml
gateways:
  - gateway_id: ha-01
    type: home_assistant
    base_url: http://homeassistant.local:8123
    api_key_ref: secret/home_assistant_token
    integration_mode: service_and_entity
```

### 7.3 传感器型设备

#### 接入方式 A：MQTT 传感器网关

适用：

- 周期上报型传感器
- 事件触发型传感器

推荐配置：

```yaml
gateways:
  - gateway_id: mqtt-sensor-01
    type: mqtt
    broker: mqtt://192.168.0.20:1883
    telemetry_topic_prefix: telemetry/
    event_topic_prefix: events/
    qos: 1
```

#### 接入方式 B：HTTP Push 网关

适用：

- 通过 webhook 上报状态的传感器平台

推荐配置：

```yaml
gateways:
  - gateway_id: http-push-sensor-01
    type: http-push
    listen_path: /ingest/http-push-sensor-01
    auth:
      type: header-secret
      header_name: X-Device-Signature
      secret_ref: secret/http_push_sensor_secret
```

### 7.4 工业设备

#### 接入方式 A：Modbus TCP 网关

适用：

- PLC
- 工业控制器
- 电力/楼控设备

推荐配置：

```yaml
gateways:
  - gateway_id: modbus-01
    type: modbus-tcp
    host: 192.168.10.20
    port: 502
    unit_ids: [1, 2, 3]
    polling_interval_ms: 1000
```

#### 接入方式 B：OPC UA 网关

适用：

- 工业信息模型较完整的设备
- SCADA/工业中台对接

推荐配置：

```yaml
gateways:
  - gateway_id: opcua-01
    type: opc-ua
    endpoint: opc.tcp://192.168.10.30:4840
    security_mode: sign_and_encrypt
    username: opcua-user
    password_ref: secret/opcua_password
```

#### 接入方式 C：BACnet/IP 网关

适用：

- 楼宇自动化设备
- 空调、楼控、照明系统

推荐配置：

```yaml
gateways:
  - gateway_id: bacnet-01
    type: bacnet-ip
    host: 192.168.10.40
    port: 47808
    device_instance_range: [1000, 1999]
```

#### 接入方式 D：CAN 网关

适用：

- 车载或工业总线设备
- 边缘控制器

推荐配置：

```yaml
gateways:
  - gateway_id: can-01
    type: can-gateway
    endpoint: tcp://192.168.10.50:7000
    bus_id: can0
    bitrate: 500000
```

## 8. 统一配置模型

平台最终应当统一为以下配置对象。

这是强制要求，不是建议项。

所有协议、所有网关、所有设备类型都必须映射到同一套通用模型上进行适配。

### 8.1 设备定义

```yaml
device_id: dev-001
device_type: conversation_terminal
protocol_type: websocket
gateway_id: null
site_id: site-shanghai-01
bind_status: bound
runtime_overrides: {}
capability_refs:
  - audio_input
  - audio_output
```

### 8.2 网关定义

```yaml
gateway_id: mqtt-sensor-01
type: mqtt
enabled: true
site_id: site-shanghai-01
auth:
  type: username_password
connection:
  broker: mqtt://192.168.0.20:1883
mapping:
  telemetry_topic_prefix: telemetry/
  event_topic_prefix: events/
```

### 8.3 能力定义

```yaml
capability_code: switch.on_off
category: actuator
properties:
  - power_state
actions:
  - turn_on
  - turn_off
events:
  - online
  - offline
```

### 8.4 网关路由定义

```yaml
gateway_route_id: route-001
device_id: dev-001
gateway_id: mqtt-sensor-01
protocol_type: mqtt
adapter_type: telemetry_ingest
direction: southbound
mapping_profile: default-temperature-sensor
enabled: true
```

### 8.5 关系映射定义

关系映射不放在设备对象自身，而由 `xuanwu-management-server` 独立维护。

```yaml
mapping_id: map-001
user_id: user-001
channel_id: channel-home-01
device_id: dev-001
agent_id: receptionist-agent
model_provider_id: provider-openai-01
model_config_id: model-gpt-realtime-01
knowledge_ids:
  - kb-home-ops
workflow_ids:
  - wf-device-escalation
enabled: true
```

### 8.6 统一事件模型

```yaml
event_id: evt-001
device_id: dev-001
gateway_id: mqtt-sensor-01
event_type: telemetry.reported
timestamp: 2026-03-30T10:30:00Z
trace_id: trace-001
payload:
  temperature: 25.1
  humidity: 48.2
```

### 8.7 统一动作调用模型

```yaml
command_id: cmd-001
device_id: dev-002
capability_code: switch.on_off
action: turn_on
arguments: {}
requested_by: agent/xuanwu-receptionist
trace_id: trace-002
```

## 9. 目录与模块规范

`xuanwu-iot-gateway` 必须采用分类型、分设备、分协议的目录布局。

目标目录形态：

```text
main/
  xuanwu-iot-gateway/
    core/
      models/
      contracts/
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
    device_profiles/
      conversation/
      actuator/
      sensor/
      industrial/
```

要求：

- 每种类型设备都要有独立网关目录
- 每种协议都要有独立适配目录
- 每类设备的配置模板和映射模板要独立存放
- 所有目录最终都实现同一套通用模型和合同接口

## 10. 设备接入流程

### 10.1 会话型设备

1. 设备通过 OTA 请求基础配置
2. `xuanwu-management-server` 返回设备可用配置
3. 设备连接 `xuanwu-device-gateway`
4. `xuanwu-device-gateway` 调 `xuanwu-management-server` 解析运行配置与关系映射
5. 管理面返回 `device + mapping + runtime_overrides`
6. `xuanwu-device-gateway` 挂载会话到 `XuanWu` Agent

### 10.2 执行型设备

1. 设备在 `xuanwu-management-server` 注册
2. 管理面维护 `user -> device`、`device -> gateway -> capability` 以及 `device -> agent` 关系
3. 可选地再通过 `user -> channel -> device` 组织这些设备的控制入口
4. `XuanWu` 中心 Agent 发出动作调用
5. `XuanWu` 调用 `xuanwu-iot-gateway`
6. `xuanwu-iot-gateway` 执行协议转换并驱动设备
7. 执行结果统一回流到 `xuanwu-management-server`

### 10.3 传感器型设备

1. 设备通过 `xuanwu-iot-gateway` 上报 telemetry/event
2. `xuanwu-iot-gateway` 使用统一事件模型标准化消息
3. `xuanwu-management-server` 统一入库、索引和发布事件
4. 规则引擎、工作流或 `XuanWu` 消费事件
5. 必要时由 `XuanWu` 再调用执行型设备

## 11. 平台级约束

### 11.1 设备不应直接做什么

- 会话型设备不承担中心决策
- 执行型设备不直接承载完整 Agent
- 传感器型设备不强行做对话

### 11.2 管理面必须承担什么

- 统一设备注册
- 统一协议抽象
- 统一权限和审计
- 统一网关治理
- 统一能力模型
- 统一事件与遥测管理

### 11.3 `XuanWu` 必须保持什么边界

- 作为 Agent 和认知真源
- 负责 Agent 实际设备调用
- 不直接成为设备注册真源
- 不直接替代管理面和网关元数据层

### 11.4 `xuanwu-iot-gateway` 必须保持什么边界

- 作为独立协议与能力适配层
- 不维护设备主档案真源
- 不维护 Agent 真源
- 不承担业务决策
- 必须实现统一事件模型、统一动作模型、统一错误模型

## 12. 目标能力声明

在本 Spec 对应的目标架构下，平台应能实现：

- 对会话型设备的中心化 Agent 管理
- 对执行型 IoT 设备的统一能力接入与调度
- 对传感器型设备的统一事件接入、统一管理与决策消费
- 对异构设备协议的分层适配
- 对工业设备的网关式纳管
- 对平台各组件的分布式部署与扩展

这意味着最终平台不是：

- 所有设备都直接运行完整 Agent

而是：

- 会话型设备是终端
- 执行型设备是能力提供者
- 传感器型设备是事件源
- `xuanwu-management-server` 是统一控制与治理平台
- `XuanWu` 是中心认知与 Agent 平面
- `xuanwu-iot-gateway` 是统一南向协议与能力适配平台

## 13. 非目标

本 Spec 当前不直接定义：

- 具体数据库表结构
- 具体网关代码实现
- 具体工业协议驱动实现细节
- 具体前端页面设计

这些会在后续 capability model、gateway contract、roadmap 文档里继续展开。
