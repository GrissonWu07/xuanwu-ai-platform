# 遥测与事件模型 Spec

## 1. 目的

本文档定义平台统一的遥测与事件模型。

目标：

- 不同协议、不同设备、不同网关的事件统一收敛
- `xuanwu-management-server` 成为事件与遥测主真源
- `XuanWu`、规则系统、工作流系统消费统一事件，而不是消费协议细节
- 支持分布式和工业化场景

## 2. 边界

### 2.1 `xuanwu-management-server`

负责：

- 遥测和事件统一接入
- 统一存储
- 统一查询
- 统一订阅
- 统一告警和规则输入

### 2.2 `xuanwu-iot-gateway`

负责：

- 接收南向原始事件
- 标准化为统一事件模型
- 上报给 `xuanwu-management-server`

### 2.3 `XuanWu`

负责：

- 消费统一事件
- 基于事件做 Agent 决策

## 3. 事件分类

平台统一事件类型分为：

- `telemetry.reported`
- `state.changed`
- `device.online`
- `device.offline`
- `alarm.triggered`
- `alarm.cleared`
- `command.result`
- `command.rejected`
- `system.health`

## 4. 统一事件模型

```yaml
event_id: evt-001
trace_id: trace-001
tenant_id: tenant-default
site_id: site-shanghai-01
user_id: user-001
channel_id: channel-home-living-room
device_id: dev-001
gateway_id: mqtt-sensor-01
event_type: telemetry.reported
event_subtype: sensor.temperature
timestamp: 2026-03-30T12:00:00Z
severity: info
source:
  protocol_type: mqtt
  adapter_type: telemetry_ingest
payload:
  temperature: 24.8
  humidity: 51.2
metadata:
  qos: 1
```

## 5. 统一遥测模型

```yaml
telemetry_id: tel-001
trace_id: trace-002
device_id: dev-001
gateway_id: mqtt-sensor-01
metric_code: sensor.temperature
timestamp: 2026-03-30T12:00:00Z
value: 24.8
unit: celsius
quality: good
tags:
  site_id: site-shanghai-01
  channel_id: channel-home-living-room
```

## 6. 命令结果事件

所有设备动作执行结果必须同时兼容“命令结果”和“事件流”。

```yaml
event_id: evt-cmd-001
trace_id: trace-003
device_id: dev-010
gateway_id: mqtt-actuator-01
event_type: command.result
timestamp: 2026-03-30T12:10:00Z
payload:
  command_id: cmd-001
  status: succeeded
  result:
    acknowledged: true
```

## 7. 告警模型

```yaml
alarm_id: alarm-001
device_id: dev-020
gateway_id: opcua-01
alarm_code: industrial.overtemperature
severity: critical
status: open
triggered_at: 2026-03-30T12:11:00Z
cleared_at: null
payload:
  temperature: 92.4
  threshold: 85
```

## 8. 遥测与事件 API 建议

建议由 `xuanwu-management-server` 提供：

- `POST /control-plane/v1/events`
- `POST /control-plane/v1/telemetry`
- `GET /control-plane/v1/events`
- `GET /control-plane/v1/events/{event_id}`
- `GET /control-plane/v1/telemetry`
- `GET /control-plane/v1/alarms`

## 9. 查询维度

所有事件与遥测至少支持以下查询维度：

- `tenant_id`
- `site_id`
- `user_id`
- `channel_id`
- `device_id`
- `gateway_id`
- `event_type`
- `severity`
- `time_from`
- `time_to`

## 10. 分布式要求

- 事件必须支持幂等写入
- 事件必须带 `event_id`
- 调用链必须带 `trace_id`
- 遥测写入必须支持高吞吐
- 查询层和写入层可分离

## 11. 非目标

- 不展开时序数据库选型
- 不展开告警规则 DSL
- 不展开前端图表设计

## 12. 最终结论

遥测与事件必须成为独立的统一模型。

没有这层：

- 传感器设备无法统一接入
- 工业设备无法统一告警
- `XuanWu` 无法稳定消费设备事件

有了这层，平台才能真正支持规则、工作流、Agent、告警和工业运维。
