# `xuanwu-portal`

`xuanwu-portal` is the unified Vue 3 frontend entrypoint for the local platform.

## Current Live Scope

Primary workspaces:

- `Overview`
- `Devices`
- `Agents`
- `Jobs`
- `Alerts`

Profile-menu workspaces:

- `Users & Roles`
- `Channels & Gateways`
- `AI Config Proxy`
- `Telemetry & Alarms`
- `Settings`
- `Sign out`

## Current Live Actions

Implemented interactive flows include:

- device discovered-item promote and ignore
- device lifecycle actions
- job pause, resume, trigger, and retry
- alarm acknowledge
- channel and gateway state actions
- detail drilldowns backed by live management APIs

## API Dependencies

The portal uses same-origin proxy paths:

- `/control-plane`
- `/gateway`
- `/runtime`
- `/jobs`

During Docker delivery, Nginx proxies these to:

- `xuanwu-management-server`
- `xuanwu-iot-gateway`
- `xuanwu-device-gateway`
- `xuanwu-jobs`

## Local Development

```bash
npm ci
npm run dev
```

Override the API base host if needed:

```bash
VITE_API_BASE_URL=http://localhost:18082
```

Runtime override is also supported:

```js
window.__XUANWU_PORTAL_API_BASE_URL__ = 'http://localhost:18082'
```

## Verification

```bash
npm test -- --run
npm run build
```

## Delivery Notes

- `xuanwu-portal` is the only frontend entrypoint.
- The browser does not need direct access to the management control secret.
- The portal container injects the control secret into proxied requests through the Nginx layer.
