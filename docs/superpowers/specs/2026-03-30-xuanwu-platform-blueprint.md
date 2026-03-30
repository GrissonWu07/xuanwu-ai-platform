# XuanWu Platform Blueprint

## Goal

定义本仓在 `XuanWu` 时代的最终本地边界，确保：

- `xuanwu-device-server` 只做会话设备运行时接入
- `xuanwu-management-server` 只做管理面、设备治理和 `XuanWu` 管理代理
- `xuanwu-gateway` 只做南向协议与能力适配
- 所有 Agent 域真源和实际设备调用决策都进入 `XuanWu`

## Modules

### xuanwu-device-server

职责：

- WebSocket / OTA / 音频运行时
- 会话设备接入
- runtime API
- 本地设备能力桥

约束：

- 不承载管理真源
- 不承载 Agent 真源
- 不再以 `AtlasClaw` 旧名作为运行时主契约

### xuanwu-management-server

职责：

- 用户、设备、频道、映射关系
- 遥测、事件、告警
- 网关目录、能力目录、能力路由
- OTA firmware / campaign
- `XuanWu` 管理代理

### xuanwu-gateway

职责：

- 南向命令标准化
- adapter registry
- `http` / `mqtt` / `home_assistant` 等协议适配
- 标准结果、事件、遥测输出

### XuanWu

职责：

- Agent 真源
- Model Provider / Model Config 真源
- Agent 决策和实际设备调用
- 调用 `xuanwu-gateway`

## Core Relations

- `user -> device` 是主归属
- `user -> channel` 是控制入口
- `channel -> device` 是组织与操作视图
- `device -> agent` 由 `xuanwu-management-server` 维护映射
- `agent -> model/provider/...` 由 `XuanWu` 维护真源

## Runtime Flow

1. 会话设备连接 `xuanwu-device-server`
2. `xuanwu-device-server` 向 `xuanwu-management-server` 拉取 runtime resolve
3. `XuanWu` 处理 Agent 逻辑
4. 若需要设备能力调用：
   - 会话设备本地能力：通过 `xuanwu-device-server runtime API`
   - 其他 IoT / southbound 能力：通过 `xuanwu-gateway`

## Local Completion Status

本仓当前已完成：

- `xuanwu-management-server` Phase 1
- `xuanwu-management-server` Phase 2
- `xuanwu-gateway` Phase 3 foundation
- `xuanwu-device-server` Phase 4 local boundary cleanup

本仓当前未完成且依赖上游：

- `XuanWu -> xuanwu-gateway` 南向命令契约联调
- `XuanWu` 采用标准 gateway 调用后，退场 `xuanwu-device-server` 中现存的 Home Assistant / IoT 兼容路径

## Source Specs

- `2026-03-28-xuanwu-device-server-rename-design.md`
- `2026-03-28-xuanwu-management-server-replacement-design.md`
- `2026-03-28-xuanwu-upstream-gap-requirements.md`
- `2026-03-30-xuanwu-gateway-foundation-design.md`
