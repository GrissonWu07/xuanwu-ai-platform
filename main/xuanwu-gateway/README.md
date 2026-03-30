# xuanwu-gateway

`xuanwu-gateway` 是本项目独立的南向协议与能力适配层。

## 当前范围

- 内建 adapter registry
- 首批 dry-run adapters:
  - `http`
  - `mqtt`
  - `home_assistant`
- 最小 API:
  - `GET /gateway/v1/adapters`
  - `POST /gateway/v1/commands:dispatch`

## 当前边界

- 上游由 `XuanWu` 产出标准能力命令
- `xuanwu-management-server` 维护网关目录、能力目录和路由
- `xuanwu-gateway` 只做命令分发和协议适配

