# Platform Implementation Roadmap

## Scope
- 把当前 spec 蓝图转换成可执行的分阶段实现路线。
- 明确本项目各模块的实现顺序、成功标准和阻塞关系。
- 保证本项目只围绕设备、管理面、网关和运行时接入实现，不侵入 `XuanWu` Agent 域真源。

## Steps
1. [x] Phase 1: `xuanwu-management-server` 基础控制面
2. [x] Phase 2: `xuanwu-management-server` 遥测 / 事件 / 网关 / OTA 治理
3. [x] Phase 3: `xuanwu-gateway` 基础模块与首批协议适配
4. [x] Phase 4: `xuanwu-device-server` 边界收口与运行时接入对齐
5. [ ] Phase 5: `XuanWu` 集成联调与契约验证

## Phase Breakdown

### Phase 1: `xuanwu-management-server` 基础控制面
目标：
- 落地最小可用控制面真源。

范围：
- 用户
- 设备
- 频道
- `user -> device`
- `user -> channel`
- `channel -> device`
- `device -> agent`
- `runtime/device-config:resolve`
- `XuanWu` 代理基础面：`agents` / `model-providers` / `models`

成功标准：
- 有独立数据模型
- 有独立 API
- 有最小测试覆盖
- `xuanwu-device-server` 能消费新的控制面结果

阶段结果：
- 已完成
- 当前验证：
  - `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-management-server/tests/test_xuanwu_proxy_contract.py -q`
  - `24 passed`

### Phase 2: `xuanwu-management-server` 遥测 / 事件 / 网关 / OTA 治理
目标：
- 落地统一治理平面。

范围：
- 统一事件入口
- 统一遥测入口
- 告警查询与确认
- 网关目录
- 能力目录
- 能力路由
- OTA firmware / campaign 基础面

成功标准：
- 事件、遥测、能力、网关、OTA 数据都由管理面主控
- 新路由不回流到 `xuanwu-device-server`

阶段结果：
- 已完成
- 当前验证：
  - `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-management-server/tests/test_xuanwu_proxy_contract.py -q`
  - `24 passed`

### Phase 3: `xuanwu-gateway` 基础模块与首批协议适配
目标：
- 落地独立南向模块。

范围：
- `main/xuanwu-gateway` 模块骨架
- contracts / registry / runtime
- 首批适配：
  - `http`
  - `mqtt`
  - `home_assistant`

成功标准：
- 能接收标准能力命令
- 能输出标准结果 / 事件 / 遥测
- 能按 adapter registry 路由到具体协议实现

阶段结果：
- 已完成
- 当前验证：
  - `python -m pytest main/xuanwu-gateway/tests/test_bootstrap.py main/xuanwu-gateway/tests/test_registry.py main/xuanwu-gateway/tests/test_dispatch.py -q`
  - `5 passed`

### Phase 4: `xuanwu-device-server` 边界收口与运行时接入对齐
目标：
- 保持 `xuanwu-device-server` 只做运行时接入。

范围：
- 清理可能回流的管理逻辑
- 对齐新的 runtime resolve
- 对齐新的控制面配置
- 对齐设备绑定和运行覆盖视图

成功标准：
- 不承载管理真源
- 不承载 Agent 真源
- 保持运行时接入链稳定

阶段结果：
- 已完成
- 当前验证：
  - `python -m pytest main/xuanwu-device-server/tests/test_local_control_plane.py main/xuanwu-device-server/tests/test_runtime_http_routes.py -q`
  - `14 passed`
- 已落地变更：
  - `AtlasClaw` 命名收口到 `XuanWu`
  - `xuanwu_session_key`
  - `XuanWuDialogueEngine`
  - `XuanWuStreamBridge`
  - `core.providers.agent.xuanwu`

### Phase 5: `XuanWu` 集成联调与契约验证
目标：
- 在不改变本项目边界的前提下完成联调。

范围：
- 代理契约验证
- 运行时 resolve 契约验证
- 设备能力调用契约验证
- 错误码与鉴权头验证

成功标准：
- 本项目完全基于 `XuanWu` 契约工作

## Verification
- command: `Get-ChildItem docs\\superpowers\\specs`
- expected: 能看到平台蓝图和所有子 spec
- actual: 已完成
- command: `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-management-server/tests/test_xuanwu_proxy_contract.py -q`
- expected: 当前基线全绿
- actual: `24 passed`

## Handoff Notes
- 当前已完成蓝图与 spec 体系。
- `Phase 1` 和 `Phase 2` 已完成。
- 后续实现默认从 `Phase 3` 开始。
- 若后续某次只做单模块实现，应再细化对应模块的独立实现计划。
