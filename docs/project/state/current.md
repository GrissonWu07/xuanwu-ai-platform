# Current State

## Objective
- 基于现有平台蓝图，把 `ai-assist-device` 推进到新的四层架构：
  - `xuanwu-device-server`
  - `xuanwu-management-server`
  - `XuanWu`
  - `xuanwu-gateway`
- 所有 Agent 域功能统一进入 `XuanWu` 需求和实现范围
- 本项目只基于 `XuanWu` API 契约完成设备治理、控制面、网关与运行时接入实现

## Completed
- 已完成平台级 spec：
  - 总蓝图
  - 目标架构
  - 管理面关系映射模型
  - 统一设备能力模型
  - `xuanwu-gateway` 合同规范
  - 遥测与事件模型
  - 生命周期与注册开通
  - 分布式部署与扩展
- 已补齐 `XuanWu` Agent 域 API 合同 spec
- 已补齐本项目侧三块蓝图：
  - `xuanwu-management-server` API 蓝图
  - `xuanwu-gateway` 模块蓝图
  - `xuanwu-device-server` 边界蓝图
- `xuanwu-management-server` 基线测试通过：
  - `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-management-server/tests/test_xuanwu_proxy_contract.py -q`
  - `15 passed`
- `xuanwu-management-server` 第一阶段基础控制面已完成：
  - 用户本地真源
  - 频道本地真源
  - 设备到 Agent 映射真源
  - 用户与频道管理 API 基础面
  - runtime resolve `binding` 视图
  - `XuanWu` 代理契约回归验证
- 当前阶段验证结果：
  - `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-management-server/tests/test_xuanwu_proxy_contract.py -q`
  - `19 passed`
- 当前阶段语法验证结果：
  - `python -m py_compile main/xuanwu-management-server/app.py main/xuanwu-management-server/core/http_server.py main/xuanwu-management-server/core/api/control_plane_handler.py main/xuanwu-management-server/core/api/xuanwu_proxy_handler.py main/xuanwu-management-server/core/store/local_store.py`
  - passed
- `xuanwu-management-server` 第二阶段最小治理切片已完成：
  - 统一事件入口
  - 统一遥测入口
  - 活跃告警目录
  - 告警确认入口
- 当前综合验证结果：
  - `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-management-server/tests/test_xuanwu_proxy_contract.py -q`
  - `22 passed`

## In Progress
- 第二阶段继续推进：
  - 网关目录
  - 能力目录与能力路由
  - OTA 治理基础面

## Risks / Decisions
- 决定：所有 Agent 域功能都放到 `XuanWu`
- 决定：设备主归属是 `user -> device`
- 决定：`channel` 是用户控制入口，不是设备主归属
- 决定：设备实际调用由 `XuanWu` 决策，经 `xuanwu-gateway` 执行
- 风险：如果本地 store 结构扩张过快，后续 Phase 2 事件/遥测/网关治理可能需要拆分子 store
- 风险：必须持续避免把 Agent 真源、管理前端逻辑重新塞入 `xuanwu-device-server`

## Next Step
- 进入 Phase 2：
  - 网关目录
  - 能力目录与能力路由
  - OTA 治理基础面
