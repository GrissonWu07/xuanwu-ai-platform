# 玄武AI中心化 Agent 物联网平台蓝图

## 1. 文档目的

本文档是当前平台级 spec 的总蓝图与统一入口。

它回答三类问题：

- 平台最终要长成什么样
- 各模块分别负责什么，不负责什么
- 已有 spec 分别覆盖了哪一块，后续应该按什么顺序继续细化

这份蓝图不替代各子 spec，而是把所有 spec 串成一张完整的架构图。

## 2. 平台目标

目标平台需要同时满足：

- 尽可能全面地管理智能设备和 IoT 设备
- 具备完整的通用物联网平台能力
- 具备完整的工业化扩展能力
- 采用中心化 Agent 架构
- 支持分布式部署、网关扩展、协议适配、统一遥测与事件治理

平台的核心理念不是“所有设备都直接运行完整 Agent”，而是：

- 会话型设备：作为 Agent 终端
- 执行型设备：作为能力提供者
- 传感器型设备：作为事件和遥测来源

## 3. 总体架构结论

最终平台由四个核心模块组成：

### 3.1 `xuanwu-device-server`

负责设备运行时与会话接入：

- 会话型设备接入
- WebSocket 实时连接
- 音频流处理
- OTA 执行入口
- 本地执行桥

不负责：

- 通用设备管理后台
- 设备目录真源
- 设备关系映射真源
- Agent 真源

### 3.2 `xuanwu-management-server`

负责管理面、控制面、目录面与统一治理：

- 用户、设备、频道、站点、分组管理
- 设备注册、开通、绑定、认领、退役
- 设备与用户、频道、Agent 的关系映射
- 遥测、事件、告警、审计统一接入与治理
- OTA 元数据与升级治理
- 网关、适配器、协议路由管理
- 对 `XuanWu` 的管理代理

它是本项目中的控制中心与设备治理真源。

### 3.3 `XuanWu`

负责中心化 Agent 认知与设备调用决策：

- Agent 真源
- Model Provider / Model Config 真源
- Knowledge / Workflow 等智能体资源真源
- Agent 运行时编排
- 基于设备能力模型进行设备调用决策

它不负责设备注册真源与设备目录真源。

### 3.4 `xuanwu-gateway`

负责南向协议和能力适配：

- 协议接入
- 设备状态标准化
- 事件标准化
- 动作调用标准化
- 工业协议桥接
- 对接第三方平台和网关

它是独立模块，不内嵌在 `xuanwu-management-server` 或 `xuanwu-device-server` 中。

## 4. 关键边界

### 4.1 设备归属

设备主归属规则是：

- `user -> device`
- 如果设备没有显式用户，则归属匿名用户 `anonymous`

### 4.2 频道作用

`channel` 不是设备主归属，而是用户的控制入口：

- `user -> channel`
- `channel -> device`

一个用户可以有多个频道，这些频道只允许管理、操作、控制该用户自己的设备。

### 4.3 Agent 绑定

设备与 Agent 的绑定由管理面维护：

- `device -> agent`
- `agent -> model provider`
- `agent -> model config`
- `agent -> knowledge`
- `agent -> workflow`

这些都属于关系映射层，不属于设备对象本身。

### 4.4 设备调用

设备实际被 Agent 调用时：

1. `xuanwu-management-server` 维护设备目录、能力、路由、映射
2. `XuanWu` 读取聚合后的映射与能力信息
3. `XuanWu` 发起标准能力调用
4. `xuanwu-gateway` 转换为具体协议动作
5. 执行结果、事件、遥测统一回流到 `xuanwu-management-server`

## 5. 设备分类模型

### 5.1 会话型设备

典型设备：

- ESP32 语音终端
- 智能音箱
- 语音面板
- AI 对讲机

角色：

- Agent 终端
- 负责语音/文本/多模态交互
- 不负责中心认知

推荐协议：

- `WebSocket`
- `MQTT Gateway`
- `HTTP OTA`

### 5.2 执行型 IoT 设备

典型设备：

- 灯
- 开关
- 窗帘
- 门锁
- 插座
- HVAC 控制器

角色：

- 能力提供者
- 由中心 Agent 或规则系统调度

推荐协议：

- `HTTP`
- `MQTT`
- `Home Assistant`

目标扩展协议：

- `Modbus TCP`
- `BACnet/IP`
- `CAN Gateway`

### 5.3 传感器型设备

典型设备：

- 温湿度传感器
- 人体存在传感器
- 门磁
- 电表
- 水表
- 工业遥测采集器

角色：

- 事件源
- 遥测源
- 状态上报源

推荐协议：

- `MQTT`
- `HTTP Push`

目标扩展协议：

- `Modbus TCP`
- `OPC UA`
- `BACnet/IP`
- `CAN Gateway`

## 6. 统一平台模型

平台必须统一以下模型：

- 设备事实模型
- 用户/设备/频道/Agent 关系映射模型
- 统一设备能力模型
- 网关合同模型
- 命令模型
- 事件模型
- 遥测模型
- 告警模型
- 生命周期与开通模型
- 分布式部署模型

## 7. 协议与网关结论

### 7.1 南向协议

当前和目标协议范围：

- `WebSocket`
- `MQTT`
- `HTTP`
- `Home Assistant`
- `Modbus TCP`
- `OPC UA`
- `BACnet/IP`
- `CAN Gateway`

### 7.2 网关原则

所有南向适配统一由 `xuanwu-gateway` 承担：

- 每种协议可独立适配
- 每种设备类型可独立建目录
- 每种设备都要映射到统一能力模型
- `XuanWu` 只看标准能力，不看厂商协议细节

## 8. 分布式结论

平台必须支持分布式部署：

- `xuanwu-device-server` 可横向扩展
- `xuanwu-management-server` 可多实例部署
- `XuanWu` 可多实例部署
- `xuanwu-gateway` 可按协议、区域、站点独立扩展

统一要求：

- 全局唯一 ID
- 标准事件总线模型
- 标准命令回执模型
- 全链路 `trace_id / request_id`

## 9. 当前完整 spec 清单

### 9.1 评估与目标架构

- [玄武AI中心化 Agent 物联网平台评估](/C:/Projects/githubs/myaiagent/ai-assist-device/docs/superpowers/specs/2026-03-30-xuanwu-central-agent-iot-platform-assessment.md)
- [玄武AI中心化 Agent 物联网平台目标架构 Spec](/C:/Projects/githubs/myaiagent/ai-assist-device/docs/superpowers/specs/2026-03-30-xuanwu-central-agent-iot-platform-target-design.md)

### 9.2 关系与统一模型

- [玄武管理面关系映射模型 Spec](/C:/Projects/githubs/myaiagent/ai-assist-device/docs/superpowers/specs/2026-03-30-xuanwu-management-mapping-model-spec.md)
- [统一设备能力模型 Spec](/C:/Projects/githubs/myaiagent/ai-assist-device/docs/superpowers/specs/2026-03-30-unified-device-capability-model-spec.md)
- [XuanWu Agent 域 API 合同 Spec](/C:/Projects/githubs/myaiagent/ai-assist-device/docs/superpowers/specs/2026-03-30-xuanwu-agent-domain-api-contract-spec.md)

### 9.3 网关与合同

- [xuanwu-gateway 合同规范 Spec](/C:/Projects/githubs/myaiagent/ai-assist-device/docs/superpowers/specs/2026-03-30-xuanwu-gateway-contract-spec.md)
- [xuanwu-gateway 模块蓝图](/C:/Projects/githubs/myaiagent/ai-assist-device/docs/superpowers/specs/2026-03-30-xuanwu-gateway-module-blueprint.md)

### 9.4 平台治理与运行

- [遥测与事件模型 Spec](/C:/Projects/githubs/myaiagent/ai-assist-device/docs/superpowers/specs/2026-03-30-telemetry-and-event-model-spec.md)
- [设备生命周期与注册开通 Spec](/C:/Projects/githubs/myaiagent/ai-assist-device/docs/superpowers/specs/2026-03-30-device-lifecycle-and-provisioning-spec.md)
- [分布式部署与扩展 Spec](/C:/Projects/githubs/myaiagent/ai-assist-device/docs/superpowers/specs/2026-03-30-distributed-deployment-and-scaling-spec.md)
- [xuanwu-management-server API 蓝图](/C:/Projects/githubs/myaiagent/ai-assist-device/docs/superpowers/specs/2026-03-30-xuanwu-management-server-api-blueprint.md)
- [xuanwu-device-server 边界蓝图](/C:/Projects/githubs/myaiagent/ai-assist-device/docs/superpowers/specs/2026-03-30-xuanwu-device-server-boundary-blueprint.md)

## 10. 推荐阅读顺序

如果你要从零开始理解整个平台，推荐顺序是：

1. 本蓝图
2. 目标架构 Spec
3. 关系映射模型 Spec
4. 统一设备能力模型 Spec
5. XuanWu Agent 域 API 合同 Spec
6. xuanwu-management-server API 蓝图
7. xuanwu-device-server 边界蓝图
8. xuanwu-gateway 合同规范 Spec
9. xuanwu-gateway 模块蓝图
10. 遥测与事件模型 Spec
11. 设备生命周期与注册开通 Spec
12. 分布式部署与扩展 Spec
13. 平台评估文档

## 11. 还未单独展开的专题

当前蓝图还缺这些独立专题 spec：

- RBAC / 多租户权限模型
- 规则引擎与事件规则 DSL
- Workflow 执行引擎合同
- Knowledge 模型与检索合同
- 审计模型
- OTA 灰度、分批、回滚策略
- xuanwu-management-server 数据模型与存储蓝图
- 设备权限与控制范围模型

## 12. 最终结论

到当前为止，这组 spec 已经构成了一套完整的平台级蓝图骨架。

它已经明确了：

- 平台分层
- 设备分类
- 设备归属
- 用户、频道、设备、Agent 的关系
- Agent 如何调用设备
- 网关如何适配协议
- 遥测和事件如何统一
- 分布式如何展开

后续继续扩展时，应始终以本蓝图为总入口，以各专题 spec 为细化依据。
