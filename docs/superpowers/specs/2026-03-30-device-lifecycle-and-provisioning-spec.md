# 设备生命周期与注册开通 Spec

## 1. 目的

本文档定义设备从注册、认领、绑定、运行到退役的完整生命周期。

目标：

- 让设备管理工业化
- 支持匿名设备、已认领设备、批量设备
- 支持会话设备、执行设备、传感器、工业设备统一生命周期

## 2. 生命周期状态

设备统一状态建议：

- `created`
- `provisioned`
- `claimed`
- `bound`
- `active`
- `suspended`
- `maintenance`
- `retired`

## 3. 状态含义

### `created`

- 设备记录已存在
- 但尚未完成配置信息下发

### `provisioned`

- 已完成设备基础配置写入
- 已具备接入条件

### `claimed`

- 设备已归属到某个用户
- 若未显式归属，则属于 `anonymous`

### `bound`

- 设备已完成平台绑定流程
- 可进入运行态

### `active`

- 设备允许参与实际运行

### `suspended`

- 设备被临时停用

### `maintenance`

- 设备处于维护模式

### `retired`

- 设备永久退出使用

## 4. 注册模型

```yaml
device_id: dev-001
user_id: anonymous
device_type: conversation_terminal
protocol_type: websocket
hardware_model: esp32-s3-box
firmware_version: 1.0.3
site_id: site-shanghai-01
lifecycle_status: provisioned
created_at: 2026-03-30T12:00:00Z
```

## 5. 认领与匿名规则

- 所有设备必须有 `user_id`
- 未认领时固定归属 `anonymous`
- 认领后从 `anonymous` 转移到真实用户
- 认领过程必须保留审计记录

## 6. 绑定流程

标准流程：

1. 设备创建
2. 设备 provisioning
3. 匿名或用户归属确认
4. bind challenge / bind code
5. 绑定成功
6. 下发运行时配置
7. 进入 active

## 7. 批量注册

平台必须支持：

- CSV/JSON 批量导入
- 按站点批量导入
- 按硬件型号批量导入
- 批量生成 provisioning token

## 8. OTA 与生命周期

OTA 升级必须与生命周期协同：

- `maintenance` 状态下优先允许升级
- `retired` 状态禁止升级
- `suspended` 状态由策略决定是否允许升级

## 9. API 建议

建议由 `xuanwu-management-server` 提供：

- `POST /control-plane/v1/devices`
- `POST /control-plane/v1/devices:batch-import`
- `POST /control-plane/v1/devices/{device_id}:claim`
- `POST /control-plane/v1/devices/{device_id}:bind`
- `POST /control-plane/v1/devices/{device_id}:suspend`
- `POST /control-plane/v1/devices/{device_id}:retire`

## 10. 审计要求

以下动作必须审计：

- 设备创建
- 设备认领
- 设备绑定
- 用户归属变更
- 生命周期状态变更
- OTA 升级

## 11. 分布式要求

- 生命周期状态变更必须幂等
- 同一设备状态切换必须避免并发冲突
- 批量导入必须支持分片执行

## 12. 最终结论

设备生命周期是平台工业化的基础。

没有生命周期管理，设备注册和控制只能停留在 demo 级；有了生命周期，才能进入批量、工业化和合规治理阶段。
