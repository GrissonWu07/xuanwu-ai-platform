# xuanwu-management-server

`xuanwu-management-server` 是新的 Python 管理宿主，用来逐步替代 legacy `manager-api` 和 `manager-web`。

## 当前已完成范围

- 独立托管 `/control-plane/v1/*`
- 提供 `XuanWu` 代理入口：
  - `/control-plane/v1/xuanwu/agents`
  - `/control-plane/v1/xuanwu/agents/{agent_id}`
  - `/control-plane/v1/xuanwu/model-providers`
  - `/control-plane/v1/xuanwu/model-providers/{provider_id}`
  - `/control-plane/v1/xuanwu/models`
  - `/control-plane/v1/xuanwu/models/{model_id}`
- 当前已支持这 3 类资源的透明 CRUD 透传

## 当前控制面真源

- `users`
- `channels`
- `devices`
- `device_agent_mappings`
- `events`
- `telemetry`
- `alarms`
- `gateways`
- `capabilities`
- `capability_routes`
- `ota_firmwares`
- `ota_campaigns`
- `runtime/device-config:resolve`

## 默认配置

- `XUANWU_MANAGEMENT_SERVER_HOST=0.0.0.0`
- `XUANWU_MANAGEMENT_SERVER_PORT=18082`
- `XUANWU_MANAGEMENT_SERVER_AUTH_KEY=xuanwu-management-local-secret`
- `XUANWU_BASE_URL=http://xuanwu-ai:8000`
- `XUANWU_CONTROL_PLANE_SECRET=xuanwu-management-to-xuanwu`

## 本地启动

```powershell
cd C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server
python app.py
```

## 当前边界

- `XuanWu`：
  - Agent 真源
  - Model Provider / Model Config 真源
  - Agent 决策与设备实际调用
- `xuanwu-management-server`：
  - 用户、设备、频道和映射关系
  - 遥测、事件、告警
  - 网关目录和能力路由
  - OTA 管理
  - `XuanWu` 管理代理
- `xuanwu-device-server`：
  - 会话设备运行时接入

## 下一步

- 进入 `xuanwu-gateway` 模块实现
- 把南向协议和设备能力适配从管理面拆成独立模块
