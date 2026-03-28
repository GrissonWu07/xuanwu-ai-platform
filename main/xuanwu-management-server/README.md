# xuanwu-management-server

`xuanwu-management-server` 是新的 Python 管理宿主，用来逐步替代 legacy `manager-api` 与 `manager-web`。

当前这一步已经完成的事情：

- 独立托管 `/control-plane/v1/*`
- 提供 `XuanWu` 代理入口：
  - `/control-plane/v1/xuanwu/agents`
  - `/control-plane/v1/xuanwu/agents/{agent_id}`
  - `/control-plane/v1/xuanwu/model-providers`
  - `/control-plane/v1/xuanwu/model-providers/{provider_id}`
  - `/control-plane/v1/xuanwu/models`
  - `/control-plane/v1/xuanwu/models/{model_id}`
- 当前已支持这 3 类资源的透明 CRUD 透传
- 支持通过环境变量配置 `XuanWu` 访问地址

当前默认配置：

- `XUANWU_MANAGEMENT_SERVER_HOST=0.0.0.0`
- `XUANWU_MANAGEMENT_SERVER_PORT=18082`
- `XUANWU_MANAGEMENT_SERVER_AUTH_KEY=xuanwu-management-local-secret`
- `XUANWU_BASE_URL=http://xuanwu-ai:8000`
- `XUANWU_CONTROL_PLANE_SECRET=xuanwu-management-to-xuanwu`

本地启动：

```powershell
cd C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server
python app.py
```

说明：

- 这里的 `XUANWU_BASE_URL` 先固定为 `http://xuanwu-ai:8000`
- 真正的 `XuanWu` 后端能力会由另一个线程继续实现
- 这个仓库当前只负责把管理宿主、访问地址和代理边界准备好
