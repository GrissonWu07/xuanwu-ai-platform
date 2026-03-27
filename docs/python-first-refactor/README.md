# Python First / AtlasClaw 重构设计总览

本目录收录本轮重构的专项设计文档，目标是将 `AtlasClaw` 提升为唯一主对话引擎，将 `xiaozhi-server` 收敛为设备接入与执行层。

## 设计范围

本轮设计覆盖以下主题：

- `AtlasClaw` 作为唯一主对话引擎的总体架构
- `session_key`、`AgentRunRequest.context`、`runtime API` 协议冻结
- `xiaozhi-runtime` provider 设计
- `xiaozhi-server` 主链路切换设计
- fallback、本地配置中心、Java 控制面下线设计

明确不在主链路中的模块：

- `manager-web`
- `manager-mobile`
- `manager-api`

以上模块在过渡期可能继续承担配置管理或历史数据访问职责，但不参与设备主对话链路。

## 文档清单

1. [AtlasClaw 主对话引擎专项设计](C:\Projects\githubs\ai-assist-deviceserver\docs\python-first-refactor\atlasclaw-main-dialogue-engine-design.md)
2. [协议与接口冻结设计](C:\Projects\githubs\ai-assist-deviceserver\docs\python-first-refactor\protocol-and-interface-freeze.md)
3. [xiaozhi-runtime Provider 设计](C:\Projects\githubs\ai-assist-deviceserver\docs\python-first-refactor\xiaozhi-runtime-provider-design.md)
4. [xiaozhi-server 主链路切换设计](C:\Projects\githubs\ai-assist-deviceserver\docs\python-first-refactor\xiaozhi-mainline-cutover-design.md)
5. [Fallback、本地配置中心与 Java 下线设计](C:\Projects\githubs\ai-assist-deviceserver\docs\python-first-refactor\fallback-config-center-and-java-sunset.md)

## 实施顺序

本轮实施顺序固定，不允许跳步：

1. 先冻结协议与接口：
   - `session_key`
   - `AgentRunRequest.context`
   - `runtime tool API`
2. 再完成 `AtlasClaw provider` 设计：
   - `xiaozhi-runtime`
3. 再改 `xiaozhi-server` 主链路：
   - 将 `startToChat()` 的主对话切到 `AtlasClaw`
4. 最后处理：
   - fallback
   - 本地配置中心
   - Java 下线

## 核心约束

- 本地工具不直接在 `xiaozhi-server` 内被“智能决定”
- 本地工具由 `AtlasClaw` 通过 runtime API 调用
- `xiaozhi-server` 不再承担主对话生成职责
- `AtlasClaw` 不作为普通 LLM provider 集成，而作为完整 Agent 引擎集成
- 实施前必须先冻结协议与接口，不允许边写代码边改契约
