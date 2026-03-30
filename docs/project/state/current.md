# Current State

## Objective
- Implement the local platform side of the four-layer architecture:
  - `xuanwu-device-server`
  - `xuanwu-management-server`
  - `xuanwu-gateway`
  - `XuanWu` integration by contract only
- Keep all Agent-domain truth in `XuanWu`.
- Finish every locally completable spec item in this repository without reintroducing legacy Java management paths.

## Completed
- Platform blueprint and active spec index are in place under `docs/superpowers/specs/`.
- `xuanwu-management-server` now provides:
  - server config APIs
  - auth login/logout
  - user, channel, and device CRUD
  - device lifecycle actions: `claim`, `bind`, `suspend`, `retire`
  - batch device import
  - mapping APIs for:
    - `user -> device`
    - `user -> channel`
    - `channel -> device`
    - `device -> agent`
    - `agent -> model provider`
    - `agent -> model config`
    - `agent -> knowledge`
    - `agent -> workflow`
  - capability, capability route, gateway, OTA firmware, OTA campaign APIs
  - runtime resolve, binding view, and capability routing view
  - chat history report and summary request persistence
  - unified event, telemetry, alarm, and gateway ingress APIs
  - query-dimension filtering for event and telemetry listing
  - command-result persistence plus mirrored `command.result` event creation
  - `XuanWu` proxy surfaces for agents, model providers, and models
- `xuanwu-gateway` now provides:
  - standalone service bootstrap
  - adapter registry
  - adapter directory skeleton by device/protocol class
  - `/gateway/v1/adapters`
  - `/gateway/v1/commands`
  - `/gateway/v1/commands:dispatch`
  - `/gateway/v1/health`
  - `/gateway/v1/config`
  - `/gateway/v1/devices/{device_id}/state`
- `xuanwu-device-server` boundary work is complete for the local phase:
  - `XuanWu` runtime naming is aligned
  - runtime context exposes `xuanwu_session_key`
  - control-plane hosting is no longer embedded back into the runtime service
  - local Python management path is the default path
  - non-upstream local test suite is now the active verification baseline
  - upstream-only `XuanWu` integration tests were removed from the local completion gate
  - current local-only coverage baseline is:
    - `config_loader.py`: 88%
    - `control_plane_handler.py`: 64%
    - selected local platform surface total: 76%

## In Progress
- No additional local-only implementation phase is open.
- Remaining work is upstream contract integration with `XuanWu`.

## Risks / Decisions
- Decision: all Agent-domain truth remains in `XuanWu`.
- Decision: `user -> device` is the primary ownership line.
- Decision: `channel` is a user control surface, not a device owner.
- Decision: actual device invocation is owned by `XuanWu`, executed through `xuanwu-gateway`.
- Risk: `xuanwu-device-server` still contains local IoT/Home Assistant compatibility code paths that should be retired only after the upstream `XuanWu -> xuanwu-gateway` contract is live.
- Risk: industrial adapters are still framework skeletons and dry-run surfaces, not full protocol implementations.

## Next Step
- Continue with upstream `XuanWu` contract alignment:
  - northbound command contract from `XuanWu` to `xuanwu-gateway`
  - management-side contract verification against `XuanWu`
  - retirement of remaining local IoT compatibility paths in `xuanwu-device-server` after upstream readiness
