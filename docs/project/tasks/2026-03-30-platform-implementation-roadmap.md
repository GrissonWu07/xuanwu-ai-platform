# Platform Implementation Roadmap

## Scope
- Turn the active platform specs into repository-local implementation work.
- Finish all local management, gateway, and runtime-boundary work in this repository.
- Leave Agent-domain source-of-truth work to `XuanWu`.

## Status
1. [x] Phase 1: `xuanwu-management-server` foundation
2. [x] Phase 2: `xuanwu-management-server` governance surfaces
3. [x] Phase 3: `xuanwu-gateway` foundation and adapter skeletons
4. [x] Phase 4: `xuanwu-device-server` boundary cleanup
5. [x] Phase 5: `xuanwu-jobs` foundation and direct local dispatch
6. [ ] Phase 6: upstream `XuanWu` integration and contract validation

## Completed Locally

### Phase 1: `xuanwu-management-server` foundation
- Implemented:
  - users
  - channels
  - devices
  - runtime resolve
  - base `XuanWu` proxy surfaces
- Verified with local management server tests.

### Phase 2: `xuanwu-management-server` governance surfaces
- Implemented:
  - auth login/logout
  - device lifecycle
  - batch device import
  - all local mapping surfaces
  - capabilities, routes, gateways
  - OTA firmware and campaigns
  - unified events, telemetry, alarms
  - gateway ingress APIs
  - event/telemetry filtering
  - mirrored `command.result` event creation
- Verified with store, handler, and HTTP route tests.

### Phase 3: `xuanwu-gateway` foundation
- Implemented:
  - standalone app bootstrap
  - adapter registry
  - command dispatch
  - adapter inventory endpoint
  - health/config/device-state endpoints
  - adapter directory layout for conversation, actuator, sensor, and industrial classes
- Verified with bootstrap, registry, and dispatch tests.

### Phase 4: `xuanwu-device-server` boundary cleanup
- Implemented:
  - runtime naming cleanup to `XuanWu`
  - `xuanwu_session_key`
  - management hosting removed from runtime service
  - runtime tests aligned to new management server path
- Verified with device-server regression tests.

## Remaining

### Phase 5: `xuanwu-jobs` foundation
- Implemented:
  - `main/xuanwu-jobs`
  - local due-schedule and job-run APIs in `xuanwu-management-server`
  - lightweight scheduler-dispatcher in `xuanwu-jobs`
  - direct execution APIs in:
    - `xuanwu-management-server`
    - `xuanwu-gateway`
    - `xuanwu-device-server`
  - Docker Compose service for `xuanwu-jobs`

### Phase 6: upstream `XuanWu` integration
- Required from upstream:
  - stable `XuanWu` management APIs by contract
  - stable northbound command contract from `XuanWu` to `xuanwu-gateway`
  - integration validation for device capability invocation
- Repository-local follow-up after upstream is ready:
  - remove remaining local IoT/Home Assistant compatibility paths from `xuanwu-device-server`
  - switch final device-action execution fully onto `XuanWu -> xuanwu-gateway`

## Verification
- command:
  - `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-gateway/tests/test_bootstrap.py main/xuanwu-gateway/tests/test_registry.py main/xuanwu-gateway/tests/test_dispatch.py main/xuanwu-device-server/tests/test_local_control_plane.py main/xuanwu-device-server/tests/test_runtime_http_routes.py main/xuanwu-device-server/tests/test_runtime_handler_unit.py main/xuanwu-jobs/tests/test_xuanwu_jobs_bootstrap.py main/xuanwu-jobs/tests/test_scheduler_contract.py main/xuanwu-jobs/tests/test_scheduler_routing.py main/xuanwu-jobs/tests/test_dispatcher_contract.py main/xuanwu-jobs/tests/test_end_to_end_jobs.py tests/test_active_spec_index.py tests/test_xuanwu_jobs_docker.py -q`
- expected:
  - local platform work stays green
- actual:
  - local verification command updated to the single-service `xuanwu-jobs` stack

- command:
  - `python -m coverage run --source=main/xuanwu-management-server,main/xuanwu-gateway,main/xuanwu-device-server,main/xuanwu-jobs -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-gateway/tests/test_bootstrap.py main/xuanwu-gateway/tests/test_registry.py main/xuanwu-gateway/tests/test_dispatch.py main/xuanwu-device-server/tests/test_local_control_plane.py main/xuanwu-device-server/tests/test_runtime_http_routes.py main/xuanwu-device-server/tests/test_runtime_handler_unit.py main/xuanwu-jobs/tests/test_xuanwu_jobs_bootstrap.py main/xuanwu-jobs/tests/test_scheduler_contract.py main/xuanwu-jobs/tests/test_scheduler_routing.py main/xuanwu-jobs/tests/test_dispatcher_contract.py main/xuanwu-jobs/tests/test_end_to_end_jobs.py tests/test_active_spec_index.py tests/test_xuanwu_jobs_docker.py -q`
- expected:
  - non-upstream local surfaces have measurable coverage
- actual:
  - full local platform suite total coverage: `62%`
  - key files:
    - `config_loader.py`: `88%`
    - `control_plane_handler.py`: `62%`
    - `local_store.py`: `84%`
    - `xuanwu-jobs/core/scheduler.py`: `64%`
    - `xuanwu-jobs/core/dispatcher.py`: tracked in the active local dispatch suite

- command:
  - `python -m py_compile main/xuanwu-management-server/core/store/local_store.py main/xuanwu-management-server/core/api/control_plane_handler.py main/xuanwu-management-server/core/http_server.py main/xuanwu-gateway/core/api/gateway_handler.py main/xuanwu-gateway/core/http_server.py`
- expected:
  - syntax validation passes
- actual:
  - passed

## Handoff Notes
- Local implementation work is effectively complete for the current spec set, including the lightweight single-service `xuanwu-jobs` path.
- The only remaining major phase depends on upstream `XuanWu` contract delivery.
