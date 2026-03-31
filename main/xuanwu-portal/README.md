# `xuanwu-portal`

`xuanwu-portal` is the unified Vue 3 frontend entrypoint for the local XuanWu platform.

## Current Scope

- `Overview`
- `Devices`
- `Agents`
- `Jobs`
- `Alerts`
- profile menu destinations:
  - `Users & Roles`
  - `Channels & Gateways`
  - `AI Config Proxy`
  - `Telemetry & Alarms`
  - `Settings`
  - `Sign out`

## Local Development

```bash
npm ci
npm run dev
```

By default the portal calls same-origin API paths such as:

- `/control-plane`
- `/gateway`
- `/runtime`
- `/jobs`

If you need to point the portal at another host during development, set:

```bash
VITE_API_BASE_URL=http://localhost:18082
```

For container or runtime overrides, the portal can also read:

```js
window.__XUANWU_PORTAL_API_BASE_URL__ = 'http://localhost:18082'
```

## Docker Delivery

The portal has a dedicated Docker image at:

- [C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-portal-deployment\main\xuanwu-portal\Dockerfile](C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-portal-deployment\main\xuanwu-portal\Dockerfile)

In the full local Docker stack it is exposed as:

- `http://localhost:18081`

Nginx forwards platform APIs to the local services:

- `/control-plane` -> `xuanwu-management-server`
- `/gateway` -> `xuanwu-gateway`
- `/runtime` -> `xuanwu-device-server`
- `/jobs` -> `xuanwu-jobs`
