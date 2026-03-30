# Current State

## Objective
- 基于现有平台蓝图，把 `ai-assist-device` 推进到新的四层架构：
  - `xuanwu-device-server`
  - `xuanwu-management-server`
  - `XuanWu`
  - `xuanwu-gateway`
- 所有 Agent 域功能统一进入 `XuanWu` 需求和实现范围。
- 本项目只基于 `XuanWu` API 契约实现设备治理、控制面、网关与运行时接入。

## Completed
- 平台级 spec 体系已补齐：
  - 总蓝图
  - 目标架构
  - 管理面关系映射模型
  - 统一设备能力模型
  - `xuanwu-gateway` 合同规范
  - 遥测与事件模型
  - 生命周期与注册开通
  - 分布式部署与扩展
- `XuanWu` Agent 域 API 合同 spec 已完成。
- 本项目侧三块蓝图已完成：
  - `xuanwu-management-server` API 蓝图
  - `xuanwu-gateway` 模块蓝图
  - `xuanwu-device-server` 边界蓝图
- `xuanwu-management-server` Phase 1 已完成：
  - 用户真源
  - 频道真源
  - 设备到 Agent 映射真源
  - 用户与频道管理 API
  - runtime resolve `binding` 视图
  - `XuanWu` 代理契约回归验证
- `xuanwu-management-server` Phase 2 已完成：
  - 统一事件入口
  - 统一遥测入口
  - 活跃告警目录
  - 告警确认入口
  - 网关目录真源与 API
  - 能力目录与能力路由真源与 API
  - OTA firmware / campaign 真源与 API
- `xuanwu-gateway` Phase 3 基础模块已完成：
  - 独立 Python 服务骨架
  - adapter registry
  - 统一命令 dispatch API
  - 首批 `http` / `mqtt` / `home_assistant` dry-run adapters
- 当前阶段验证结果：
  - `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-management-server/tests/test_xuanwu_proxy_contract.py main/xuanwu-gateway/tests/test_bootstrap.py main/xuanwu-gateway/tests/test_registry.py main/xuanwu-gateway/tests/test_dispatch.py -q`
  - `29 passed`
- 当前阶段语法验证结果：
  - `python -m py_compile main/xuanwu-management-server/app.py main/xuanwu-management-server/core/http_server.py main/xuanwu-management-server/core/api/control_plane_handler.py main/xuanwu-management-server/core/api/xuanwu_proxy_handler.py main/xuanwu-management-server/core/store/local_store.py`
  - passed
  - `python -m py_compile main/xuanwu-gateway/app.py main/xuanwu-gateway/core/http_server.py main/xuanwu-gateway/core/api/gateway_handler.py main/xuanwu-gateway/core/registry/adapter_registry.py main/xuanwu-gateway/core/contracts/models.py main/xuanwu-gateway/core/adapters/base.py main/xuanwu-gateway/core/adapters/http_adapter.py main/xuanwu-gateway/core/adapters/mqtt_adapter.py main/xuanwu-gateway/core/adapters/home_assistant_adapter.py`
  - passed

## In Progress
- 准备进入 `Phase 4`：
  - `xuanwu-device-server` 边界复核
  - runtime resolve 对齐新治理字段
  - 清理仍可本地收口的旧运行时耦合

## Risks / Decisions
- 决定：所有 Agent 域功能都放到 `XuanWu`。
- 决定：设备主归属是 `user -> device`。
- 决定：`channel` 是用户控制入口，不是设备主归属。
- 决定：设备实际调用由 `XuanWu` 决策，经 `xuanwu-gateway` 执行。
- 风险：后续 `xuanwu-gateway` 的协议适配若直接耦合管理层模型，可能破坏边界。
- 风险：必须持续避免把 Agent 真源或管理前端逻辑重新塞回 `xuanwu-device-server`。

## Next Step
- 进入 `Phase 4`
- 复核 `xuanwu-device-server` 是否仍残留管理或协议适配耦合
- 对齐 `xuanwu-management-server` 新增的治理字段消费边界
