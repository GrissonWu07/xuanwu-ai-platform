# xuanwu-device-gateway 边界蓝图

## 1. 目的

本文档定义 `xuanwu-device-gateway` 在最终平台中的职责边界，确保它只承担运行时接入职责，不重新吸收管理面和 Agent 域能力。

## 2. 保留职责

`xuanwu-device-gateway` 继续负责：

- 会话型设备接入
- WebSocket 实时会话
- 音频流处理
- OTA 执行入口
- 本地执行桥
- 会话级状态和连接生命周期管理

## 3. 明确不再承担

不再承担：

- 设备目录真源
- 用户与设备关系真源
- Agent 域配置真源
- 管理后台
- 控制面 API 宿主
- 遥测与事件治理真源
- 通用 IoT 协议适配

## 4. 依赖关系

### 4.1 对 `xuanwu-management-server`

依赖这些能力：

- 设备配置解析
- 绑定与运行时视图
- OTA 元数据
- 控制密钥和运行覆盖参数

### 4.2 对 `XuanWu`

不应直接依赖其管理真源。

如需 Agent 运行时配置，应通过：

- `xuanwu-management-server` 聚合视图
- 或经其代理后的 `XuanWu` 运行结果

### 4.3 对 `xuanwu-iot-gateway`

原则上不直接承担通用网关职责。

## 5. 外部接口边界

### 5.1 应保留

- `/xuanwu/v1/`
- `/xuanwu/ota/`
- 设备接入与会话运行路径

### 5.2 应移出

- `/control-plane/v1/*`
- 管理后台页面入口
- 通用 IoT 管理接口

## 6. 设备模型边界

本模块可以持有的，是运行期设备上下文：

- `device_id`
- `client_id`
- `session_key`
- `runtime_session_id`
- 连接态
- 当前 turn / stream / interrupt 状态

本模块不应成为这些对象的真源：

- `user`
- `channel`
- `agent`
- `knowledge`
- `workflow`
- `gateway route`

## 7. 运行链路

推荐链路：

1. 会话设备连接到 `xuanwu-device-gateway`
2. `xuanwu-device-gateway` 调 `xuanwu-management-server` 解析设备运行绑定
3. 获取设备归属、Agent 绑定、运行覆盖信息
4. 会话运行期如需 Agent 能力，则由上游 `XuanWu` 承担
5. 设备控制实际执行走 `XuanWu -> xuanwu-iot-gateway`

## 8. 后续实现要求

实现中必须持续检查：

- 不把管理逻辑重新塞回 `xuanwu-device-gateway`
- 不把 Agent 配置真源重新塞回 `xuanwu-device-gateway`
- 不把通用 IoT 网关逻辑塞回 `xuanwu-device-gateway`

## 9. 结论

`xuanwu-device-gateway` 的最终形态应该是“会话设备运行时接入服务”，而不是“万能平台宿主”。
