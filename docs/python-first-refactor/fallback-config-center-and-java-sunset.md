# Fallback、本地配置中心与 Java 下线设计

> 迁移补充说明（2026-03-28）
>
> 当前仓库里的 Python 控制面宿主已经明确为 `main/xuanwu-management-server`，不再建议把新的控制面实现继续塞回 `xuanwu-device-gateway`。
>
> 当前 `XuanWu` 服务访问地址先固定为 `http://xuanwu-ai:8000`，由 `xuanwu-management-server` 通过 `/control-plane/v1/xuanwu/*` 代理入口统一转发。
>
> 当前 `manager-api` 只保留显式兼容模式：只有 `manager-api.enabled=true` 且 `url` 已配置时，`xuanwu-device-gateway` 才会回退到 Java 配置源。

## 1. 目的

本文档覆盖实施顺序中的最后一阶段：

- fallback
- 本地配置中心
- Java 控制面下线

这些能力不参与第一阶段主链路切换，但必须提前设计清楚，避免主链路切换后架构悬空。

## 2. Fallback 设计

### 2.1 目标

当 `AtlasClaw` 不可用时，系统不能完全瘫痪，至少要维持：

- 基础语音交互
- 错误说明
- 少量本地工具能力

### 2.2 fallback 分级

#### Level 0: 无回退

- 直接报错
- 只适合测试环境

#### Level 1: 最小对话回退

- 固定模板回复
- 简单说明远端不可用
- 不做复杂代理任务

#### Level 2: 轻量本地代理回退

- 复用当前本地 `LLM + Intent + UnifiedToolHandler`
- 仅支持基础能力
- 不保证与 `AtlasClaw` 记忆一致

推荐默认采用：

- `Level 1` 先落地
- `Level 2` 作为后续增强

### 2.3 fallback 触发条件

- `AtlasClaw /agent/run` 不可达
- SSE stream 建立失败
- 远端超时
- 服务间认证失败

### 2.4 fallback 原则

- fallback 是保底机制，不是第二主引擎
- 正常情况下绝不与 `AtlasClaw` 并行主导
- fallback 恢复后会话不自动合并到远端

## 3. 本地配置中心设计

### 3.1 背景

当前 `xuanwu-server` 仍依赖 `manager-api`：

- `/config/server-base`
- `/config/agent-models`

要想彻底切掉 Java，必须先在 Python 侧建立控制面。

### 3.2 目标

建立 Python 本地配置中心，承担：

- server 公共配置
- 设备绑定配置
- agent profile
- 模型映射配置
- 知识库映射配置
- runtime secret

### 3.3 建议存储形态

第一阶段使用本地文件：

- `data/server_config.yaml`
- `data/devices/{device_id}.yaml`
- `data/agents/{agent_id}.yaml`
- `data/models/*.yaml`

后续如需升级，可换 SQLite/PostgreSQL，但接口层不变。

### 3.4 最小 Python 控制面 API

统一前缀：

- `/control-plane/v1`

建议最小接口：

- `GET /control-plane/v1/config/server`
- `PUT /control-plane/v1/config/server`
- `GET /control-plane/v1/devices/{device_id}`
- `PUT /control-plane/v1/devices/{device_id}`
- `GET /control-plane/v1/agents/{agent_id}`
- `PUT /control-plane/v1/agents/{agent_id}`
- `POST /control-plane/v1/runtime/device-config:resolve`

### 3.5 与主链路关系

主链路切换到 `AtlasClaw` 后：

- 控制面只负责配置与解析
- 不参与主对话生成
- 不插入设备音频链路

## 4. Java 控制面下线设计

### 4.1 不参与主链路的明确结论

以下模块不参与主对话链路：

- `manager-web`
- `manager-api`

主链路切换完成后，这些模块最多只作为：

- 临时配置迁移来源
- 数据导出来源
- 历史后台系统

### 4.2 Java 当前承担的控制面范围

当前 `manager-api` 主要提供：

- `config/server-base`
- `config/agent-models`
- 设备绑定
- 设备工具调用
- 知识库管理
- 模型配置
- 用户与安全

其中与主对话重构直接相关的优先迁移项是：

1. 配置解析
2. 设备绑定
3. 模型映射
4. runtime secret

### 4.3 下线顺序

#### Stage 1: 切断主链路依赖

- `xuanwu-server` 不再调用 `manager-api` 获取主对话相关配置
- `AtlasClaw` 主对话完全独立

#### Stage 2: 迁移控制面最小能力

- 迁移 `server-base`
- 迁移 `agent-models`
- 迁移设备绑定
- 迁移关键密钥配置

#### Stage 3: 只读过渡

- Java API 仅用于历史数据查询
- 不再作为运行依赖

#### Stage 4: 下线

- 关闭 `manager-web`
- 关闭 `manager-api`

### 4.4 数据迁移建议

建议先做导出脚本，迁移以下对象：

- 设备列表
- Agent 配置
- 模型配置
- 知识库配置
- 绑定关系

## 5. 实施顺序回放

本轮必须严格遵循以下顺序：

1. 先完成协议与接口设计冻结
   - `session_key`
   - `AgentRunRequest.context`
   - `runtime tool API`
2. 再完成 `AtlasClaw provider` 设计
   - `xuanwu-runtime`
3. 再改 `xuanwu-server` 主链路
   - `startToChat()` 切到 `AtlasClaw`
4. 最后处理
   - fallback
   - 本地配置中心
   - Java 下线

这个顺序不能颠倒，原因是：

- 接口未冻结前，provider 无法稳定实现
- provider 未设计前，主链路切换没有执行层
- 主链路未切换前，fallback 与 Java 下线没有可靠边界

## 6. 最终目标架构

最终形态：

- `AtlasClaw`：唯一主对话引擎
- `xuanwu-server`：设备接入与执行层
- Python 控制面：配置、设备、agent、model、secret
- Java / Web：完全退出主链路，并最终下线

## 7. 验收标准

- `AtlasClaw` 不可用时有明确 fallback
- `xuanwu-server` 不再依赖 `manager-api` 获取主链路配置
- `manager-web`、`manager-api` 不参与主对话路径
- Java 可以进入只读过渡再最终下线


