# 玄武管理面关系映射模型 Spec

## 1. 目的

本文档定义 `xuanwu-management-server` 负责维护的关系映射模型。

目标是把以下几类信息从“设备自身对象”里剥离出来，改为由管理面统一维护：

- 用户与设备
- 用户与频道
- 频道与设备
- 设备与 Agent
- Agent 与 Model Provider / Model Config
- Agent 与 Knowledge
- Agent 与 Workflow

这份文档的核心原则是：

- 设备对象只描述设备自身事实
- Agent 对象只描述 Agent 自身事实
- 所有跨对象绑定关系都由 `xuanwu-management-server` 维护

## 2. 设计原则

### 2.1 设备不持有业务绑定真源

设备模型不应直接持有以下字段作为真源：

- `agent_mode`
- `agent_id`
- `channel_id`
- `workflow_id`
- `knowledge_id`
- `model_config_id`

原因：

- 这些字段本质上是“关系”，不是“设备事实”
- 一个设备未来可能被重新分配给不同 Agent
- 一个 Agent 也可能被多个设备或多个频道复用
- 如果把关系塞进设备对象，会让设备模型承担过多业务语义

### 2.2 管理面是关系映射主真源

`xuanwu-management-server` 必须成为以下映射关系的主真源：

- `user -> device`
- `user -> channel`
- `channel -> device`
- `device -> agent`
- `agent -> model provider`
- `agent -> model config`
- `agent -> knowledge`
- `agent -> workflow`

### 2.3 XuanWu 不维护设备业务目录

`XuanWu` 的职责是：

- 维护 Agent、Model Provider、Model Config 真源
- 在运行时消费管理面下发的关系映射结果
- 根据映射关系执行设备调用

`XuanWu` 不应自行维护：

- 设备注册主档案
- 设备绑定主档案
- 用户到设备的业务映射真源

## 3. 对象边界

### 3.1 设备对象

设备对象只保留设备自身事实。

推荐字段：

```yaml
device_id: dev-001
device_type: conversation_terminal
protocol_type: websocket
gateway_id: null
site_id: site-shanghai-01
hardware_model: esp32-s3-box
firmware_version: 1.0.3
bind_status: bound
capability_refs:
  - audio_input
  - audio_output
runtime_overrides: {}
```

不应作为设备事实字段的内容：

- 当前归属哪个 Agent
- 当前使用哪个 Model Config
- 当前关联哪个 Workflow

### 3.2 Agent 对象

Agent 对象只保留 Agent 自身事实。

推荐字段：

```yaml
agent_id: receptionist-agent
name: 前台接待
description: 用于访客接待与设备接入引导
status: active
version: 3
```

Agent 不应自行持有：

- 某个具体设备列表
- 某个具体频道列表

这些属于关系层。

### 3.3 用户对象

用户对象只描述用户身份和权限范围。

推荐字段：

```yaml
user_id: user-001
tenant_id: tenant-default
name: 张三
roles:
  - admin
status: active
```

匿名用户规则：

- 如果设备没有绑定到显式用户
- 则设备必须归属到匿名用户
- 推荐固定匿名用户 ID：`anonymous`
- 匿名用户也是正式用户对象，而不是空值或缺省状态

### 3.4 Channel 对象

`Channel` 是用户名下的逻辑控制入口，不是独立于用户存在的设备归属主体。

`Channel` 可以表示：

- 家庭空间
- 站点
- 房间
- 业务入口
- 终端分组
- 会话入口

推荐字段：

```yaml
channel_id: channel-home-living-room
tenant_id: tenant-default
channel_type: room
name: 客厅
status: active
```

约束：

- 每个 `Channel` 必须归属于某个 `User`
- 一个 `User` 可以拥有多个 `Channel`
- `Channel` 只能管理、操作、控制该 `User` 自己名下的设备
- `Channel` 不能跨用户直接引用别人的设备

## 4. 关系映射模型

### 4.1 UserDeviceMapping

定义设备直接归属于哪个用户。

```yaml
mapping_id: map-user-device-001
user_id: user-001
device_id: dev-001
role: owner
enabled: true
```

规则：

- 每个设备必须至少有一条 `UserDeviceMapping`
- 如果没有显式用户，则必须自动落到：
  - `user_id: anonymous`
- 不允许设备处于“无用户归属”的悬空状态

用途：

- 设备主归属
- 用户名下设备清单
- 匿名设备管理
- 后续租户、权限和计费边界

### 4.2 UserChannelMapping

定义用户可进入哪些逻辑入口。

```yaml
mapping_id: map-user-channel-001
user_id: user-001
channel_id: channel-home-living-room
role: owner
enabled: true
```

用途：

- 用户权限控制
- 多租户和多站点访问边界
- 前端可见范围控制
- 定义“某个用户拥有多个控制入口”

### 4.3 ChannelDeviceMapping

定义某个频道下有哪些设备。

说明：

- 这是用户设备的二级组织关系
- 设备的主归属仍然是 `user -> device`
- `channel -> device` 用于把“该用户自己的设备”组织进不同控制入口
- `channel -> device` 不允许越过 `user -> device` 的主归属边界
- 一个用户的多个 `Channel` 可以分别管理、操作、控制该用户自己的不同设备子集，或相同设备子集

```yaml
mapping_id: map-channel-device-001
channel_id: channel-home-living-room
device_id: dev-001
enabled: true
priority: 100
```

用途：

- 房间/场景/空间内设备组织
- UI 聚合展示
- 用户多入口控制

### 4.4 DeviceAgentMapping

定义某个设备在当前业务上下文下绑定哪个 Agent。

```yaml
mapping_id: map-device-agent-001
device_id: dev-001
agent_id: receptionist-agent
enabled: true
priority: 100
effective_from: null
effective_to: null
```

说明：

- 一个设备可以存在多条候选映射
- 实际生效关系由优先级、状态和时间窗口决定

### 4.5 AgentModelProviderMapping

定义 Agent 默认使用哪个模型提供方。

```yaml
mapping_id: map-agent-provider-001
agent_id: receptionist-agent
model_provider_id: provider-openai-01
enabled: true
```

### 4.6 AgentModelConfigMapping

定义 Agent 运行时使用哪个具体模型配置。

```yaml
mapping_id: map-agent-model-001
agent_id: receptionist-agent
model_config_id: model-gpt-realtime-01
purpose: primary
enabled: true
```

### 4.7 AgentKnowledgeMapping

定义 Agent 可用的知识域。

```yaml
mapping_id: map-agent-knowledge-001
agent_id: receptionist-agent
knowledge_id: kb-home-ops
enabled: true
```

### 4.8 AgentWorkflowMapping

定义 Agent 可用的工作流。

```yaml
mapping_id: map-agent-workflow-001
agent_id: receptionist-agent
workflow_id: wf-device-escalation
enabled: true
```

## 5. 聚合视图模型

为了便于运行时消费，`xuanwu-management-server` 需要把多张关系映射聚合成统一视图，而不是让运行时逐表查。

### 5.1 DeviceRuntimeBindingView

这是运行时最关键的视图。

```yaml
device_id: dev-001
user_id: user-001
channel_id: channel-home-living-room
agent_id: receptionist-agent
model_provider_id: provider-openai-01
model_config_id: model-gpt-realtime-01
knowledge_ids:
  - kb-home-ops
workflow_ids:
  - wf-device-escalation
gateway_ids: []
runtime_overrides: {}
```

说明：

- `user_id` 是设备主归属
- `channel_id` 是当前控制入口，不改变设备主归属

这个视图应由 `xuanwu-management-server` 生成并返回给：

- `xuanwu-device-gateway`
- `XuanWu`

### 5.2 DeviceCapabilityRoutingView

这是设备能力调用阶段的聚合视图。

```yaml
device_id: dev-010
device_type: actuator
gateway_id: mqtt-actuator-01
capability_refs:
  - switch.on_off
  - light.brightness
command_route:
  protocol_type: mqtt
  mapping_profile: default-light-device
```

这个视图用于：

- `XuanWu` 决定要调用哪个设备能力
- `xuanwu-iot-gateway` 知道如何路由到实际设备

## 6. 优先级与覆盖规则

### 6.1 关系覆盖顺序

如果未来同时存在多层关系来源，推荐覆盖顺序如下：

1. tenant 级默认关系
2. user 级关系
3. channel 级关系
4. device 级关系
5. runtime 临时覆盖

最终运行时看到的是覆盖后的聚合视图，而不是原始多层对象。

### 6.2 冲突规则

如果多个映射同时命中：

- 先按 `enabled=true`
- 再按 `effective_from/effective_to`
- 再按 `priority` 由高到低
- 若仍冲突，则返回配置冲突错误，不允许静默猜测

## 7. API 责任划分

### 7.1 xuanwu-management-server

负责提供：

- 用户、频道、设备、映射关系的管理 API
- 聚合视图 API
- 设备注册和绑定 API
- 事件与遥测查询 API

### 7.2 XuanWu

负责提供：

- Agent / Model Provider / Model Config 真源 API
- 基于聚合视图的设备调用执行逻辑

### 7.3 xuanwu-iot-gateway

负责提供：

- 统一设备调用入口
- 协议适配
- 统一执行回执
- 遥测和事件标准化回流

## 8. 最小 API 视图建议

### 8.1 管理面聚合视图接口

建议由 `xuanwu-management-server` 提供：

- `GET /control-plane/v1/runtime/device-bindings/{device_id}`
- `GET /control-plane/v1/runtime/device-capability-routes/{device_id}`

### 8.2 管理面关系管理接口

建议由 `xuanwu-management-server` 提供：

- `GET /control-plane/v1/mappings/user-devices`
- `GET /control-plane/v1/mappings/user-channels`
- `GET /control-plane/v1/mappings/channel-devices`
- `GET /control-plane/v1/mappings/device-agents`
- `GET /control-plane/v1/mappings/agent-model-providers`
- `GET /control-plane/v1/mappings/agent-models`
- `GET /control-plane/v1/mappings/agent-knowledge`
- `GET /control-plane/v1/mappings/agent-workflows`

## 9. 非目标

本 Spec 当前不展开：

- 数据库表结构
- 多租户权限细节
- Workflow / Knowledge 自身模型定义
- 前端页面结构

这些内容应在后续子 spec 中继续细化。

## 10. 最终结论

`agent_mode` 不应属于设备对象。

更合理的方式是：

- 设备对象只描述设备自身
- `xuanwu-management-server` 维护所有跨域关系映射
- 设备首先直接归属到用户；没有用户时归属匿名用户
- `channel` 是用户名下的控制入口，一个用户可以有多个 `channel`
- 这些 `channel` 只管理、操作、控制该用户自己的设备
- `xuanwu-device-gateway` 消费聚合后的运行时关系结果
- `XuanWu` 基于这些关系结果完成 Agent 决策和设备调用
- `xuanwu-iot-gateway` 负责完成实际协议执行

这套关系映射模型，是后续建设完整中心化 Agent 物联网平台的必要基础。
