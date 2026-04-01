# 统一设备能力模型 Spec

## 1. 目的

本文档定义平台统一设备能力模型。

目标：

- 不同协议、不同设备、不同厂商都映射到统一能力模型
- `XuanWu` 调用设备时不关心协议细节
- `xuanwu-management-server` 可以统一管理设备能力
- `xuanwu-iot-gateway` 可以统一路由和执行

## 2. 基本原则

- 设备类型不等于能力类型
- 协议不等于能力类型
- 一个设备可以有多个能力
- 一个能力可以由多个协议实现
- Agent 只调用标准能力，不直接拼协议细节

## 3. 核心对象

### 3.1 DeviceType

固定设备大类：

- `conversation_terminal`
- `actuator`
- `sensor`
- `industrial_controller`

### 3.2 CapabilityCategory

固定能力大类：

- `interaction`
- `actuation`
- `telemetry`
- `state`
- `vision`
- `audio`
- `system`

### 3.3 CapabilityDefinition

统一能力定义：

```yaml
capability_code: switch.on_off
name: 开关控制
category: actuation
device_types:
  - actuator
properties:
  - power_state
actions:
  - turn_on
  - turn_off
events:
  - state_changed
```

## 4. 能力结构

每个能力由四部分组成：

- 属性 `properties`
- 动作 `actions`
- 事件 `events`
- 遥测 `telemetry`

### 4.1 属性

属性用于表示当前状态。

示例：

- `power_state`
- `brightness`
- `temperature`
- `humidity`
- `lock_state`

### 4.2 动作

动作用于驱动设备执行操作。

示例：

- `turn_on`
- `turn_off`
- `set_brightness`
- `lock`
- `unlock`

### 4.3 事件

事件用于表达状态变化或重要信号。

示例：

- `online`
- `offline`
- `state_changed`
- `alarm_triggered`

### 4.4 遥测

遥测用于周期或流式上报。

示例：

- `temperature`
- `humidity`
- `energy_usage`
- `vibration_level`

## 5. 标准能力集合

### 5.1 会话型设备能力

#### `audio.input`

```yaml
capability_code: audio.input
category: audio
properties:
  - sample_rate
  - channels
actions: []
events:
  - audio_frame_received
telemetry: []
```

#### `audio.output`

```yaml
capability_code: audio.output
category: audio
properties:
  - volume
actions:
  - play_audio
  - stop_audio
events:
  - playback_started
  - playback_finished
telemetry: []
```

#### `interaction.wakeup`

```yaml
capability_code: interaction.wakeup
category: interaction
properties:
  - wakeup_enabled
actions:
  - enable_wakeup
  - disable_wakeup
events:
  - wakeup_detected
telemetry: []
```

### 5.2 执行型设备能力

#### `switch.on_off`

```yaml
capability_code: switch.on_off
category: actuation
properties:
  - power_state
actions:
  - turn_on
  - turn_off
events:
  - state_changed
telemetry: []
```

#### `light.brightness`

```yaml
capability_code: light.brightness
category: actuation
properties:
  - brightness
actions:
  - set_brightness
events:
  - brightness_changed
telemetry: []
```

#### `lock.control`

```yaml
capability_code: lock.control
category: actuation
properties:
  - lock_state
actions:
  - lock
  - unlock
events:
  - lock_state_changed
telemetry: []
```

### 5.3 传感器型设备能力

#### `sensor.temperature`

```yaml
capability_code: sensor.temperature
category: telemetry
properties:
  - last_temperature
actions: []
events:
  - threshold_exceeded
telemetry:
  - temperature
```

#### `sensor.humidity`

```yaml
capability_code: sensor.humidity
category: telemetry
properties:
  - last_humidity
actions: []
events:
  - threshold_exceeded
telemetry:
  - humidity
```

#### `sensor.occupancy`

```yaml
capability_code: sensor.occupancy
category: telemetry
properties:
  - occupied
actions: []
events:
  - occupancy_changed
telemetry:
  - occupied
```

### 5.4 工业设备能力

#### `industrial.register`

```yaml
capability_code: industrial.register
category: telemetry
properties:
  - register_value
actions:
  - write_register
events:
  - register_changed
telemetry:
  - register_value
```

#### `industrial.alarm`

```yaml
capability_code: industrial.alarm
category: state
properties:
  - alarm_state
actions:
  - acknowledge_alarm
events:
  - alarm_triggered
  - alarm_cleared
telemetry: []
```

## 6. 设备能力绑定

设备不直接发明自己的能力模型，而是引用标准能力定义。

示例：

```yaml
device_id: dev-010
capability_refs:
  - switch.on_off
  - light.brightness
```

## 7. 能力路由

每个能力必须绑定到具体网关路由。

示例：

```yaml
device_id: dev-010
capability_code: switch.on_off
gateway_id: mqtt-actuator-01
protocol_type: mqtt
mapping_profile: default-light-device
```

## 8. Agent 调用约束

`XuanWu` 调用设备时必须遵守：

- 只能调用标准能力代码
- 不能直接构造厂商协议负载
- 不能跳过 `xuanwu-iot-gateway`
- 不能绕过 `xuanwu-management-server` 的能力与路由视图

## 9. 配置校验规则

### 9.1 设备校验

- 每个设备至少一个标准能力
- 每个能力必须有路由
- 每个路由必须绑定一个网关

### 9.2 能力校验

- `capability_code` 全局唯一
- `action` 名称在能力内唯一
- `property` 名称在能力内唯一

### 9.3 调用校验

- `action` 必须属于该能力
- 设备必须声明该能力
- 路由必须处于 `enabled=true`

## 10. 管理面职责

`xuanwu-management-server` 负责：

- 维护能力定义目录
- 维护设备能力引用
- 维护能力路由
- 为 `XuanWu` 提供聚合视图

## 11. 网关职责

`xuanwu-iot-gateway` 负责：

- 把标准能力动作映射成协议动作
- 把协议状态映射成标准属性
- 把协议事件映射成标准事件
- 把协议遥测映射成标准遥测

## 12. 聚合视图建议

建议由 `xuanwu-management-server` 提供：

- `GET /control-plane/v1/capabilities`
- `GET /control-plane/v1/devices/{device_id}/capabilities`
- `GET /control-plane/v1/devices/{device_id}/capability-routes`

## 13. 非目标

本 Spec 当前不展开：

- UI 页面设计
- 厂商私有字段全集
- 单个工业协议寄存器细节

## 14. 最终结论

统一设备能力模型是整个平台的核心抽象层。

没有这层：

- `XuanWu` 会被迫理解各类协议细节
- `xuanwu-management-server` 无法统一管理异构设备
- `xuanwu-iot-gateway` 无法形成可复用的标准适配框架

有了这层：

- 设备事实、关系映射、Agent 决策、协议执行四层才能真正解耦。
