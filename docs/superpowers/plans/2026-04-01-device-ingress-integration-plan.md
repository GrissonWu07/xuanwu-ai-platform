# Device Ingress Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement unified device discovery, registration, heartbeat, and promotion flows across `xuanwu-management-server`, `xuanwu-iot-gateway`, `xuanwu-device-gateway`, and `xuanwu-portal`.

**Architecture:** Add a new `discovered_device` layer inside `xuanwu-management-server`, wire ingress callbacks from gateway and device-server into that store, expand managed device aggregation with recency and provenance fields, then expose portal surfaces for pending-device review and promotion into managed devices. Keep execution ownership unchanged: ingress services discover and report, management owns durable truth.

**Tech Stack:** Python, aiohttp, YAML-backed local store, Vue 3, Vitest, pytest

---

### Task 1: Add discovered-device persistence and promotion logic

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-management-server\core\store\local_store.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-management-server\tests\test_local_control_plane.py`

- [ ] **Step 1: Write failing store tests for discovered-device lifecycle**

Add tests covering:
- creating a discovered device
- updating last seen on repeat discovery
- promoting a discovered device into a managed device
- updating managed-device recency fields from heartbeat

- [ ] **Step 2: Run the focused store tests to verify failure**

Run:

```powershell
python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py -q
```

Expected: failures for missing discovered-device store methods and missing recency updates.

- [ ] **Step 3: Implement discovered-device store and promotion helpers**

Implement in `local_store.py`:
- create `discovered_devices` directory in `__init__`
- add:
  - `get_discovered_device()`
  - `list_discovered_devices()`
  - `save_discovered_device()`
  - `promote_discovered_device()`
  - `ignore_discovered_device()`
  - `update_device_heartbeat()`
- extend managed-device records with:
  - `device_kind`
  - `ingress_type`
  - `gateway_id`
  - `protocol_type`
  - `adapter_type`
  - `runtime_endpoint`
  - `last_seen_at`
  - `last_event_at`
  - `last_telemetry_at`
  - `last_command_at`

- [ ] **Step 4: Re-run focused store tests**

Run:

```powershell
python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py -q
```

Expected: store tests pass.

- [ ] **Step 5: Commit**

```powershell
git add main/xuanwu-management-server/core/store/local_store.py main/xuanwu-management-server/tests/test_local_control_plane.py
git commit -m "feat: add discovered device persistence"
```

### Task 2: Add management APIs for discovery, heartbeat, and richer device detail

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-management-server\core\api\control_plane_handler.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-management-server\core\http_server.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-management-server\tests\test_http_routes.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-management-server\tests\test_local_control_plane.py`

- [ ] **Step 1: Write failing API tests**

Add tests for:
- `GET /control-plane/v1/discovered-devices`
- `POST /control-plane/v1/discovered-devices`
- `GET /control-plane/v1/discovered-devices/{discovery_id}`
- `POST /control-plane/v1/discovered-devices/{discovery_id}:promote`
- `POST /control-plane/v1/discovered-devices/{discovery_id}:ignore`
- `POST /control-plane/v1/devices/{device_id}:heartbeat`
- expanded device-detail response including discovery provenance and latest command result

- [ ] **Step 2: Run the focused route tests to verify failure**

Run:

```powershell
python -m pytest main/xuanwu-management-server/tests/test_http_routes.py -q
```

Expected: failures for missing routes and response fields.

- [ ] **Step 3: Implement handler methods and routes**

Implement:
- discovered-device collection/item handlers
- promote/ignore handlers
- heartbeat handler
- `build_device_detail()` expansion in store as needed
- route registration in `http_server.py`

- [ ] **Step 4: Re-run route and store tests**

Run:

```powershell
python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py -q
```

Expected: both suites pass.

- [ ] **Step 5: Commit**

```powershell
git add main/xuanwu-management-server/core/api/control_plane_handler.py main/xuanwu-management-server/core/http_server.py main/xuanwu-management-server/core/store/local_store.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-management-server/tests/test_local_control_plane.py
git commit -m "feat: add device discovery management APIs"
```

### Task 3: Add gateway discovery and heartbeat callbacks

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-iot-gateway\core\clients\management_client.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-iot-gateway\core\api\gateway_handler.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-iot-gateway\tests\test_dispatch.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-iot-gateway\tests\test_sensor_ingest.py`

- [ ] **Step 1: Write failing gateway tests**

Add tests for:
- gateway callback client posting discovered devices
- gateway callback client posting device heartbeat
- ingest path ensuring unknown device callbacks can trigger discovery
- command path ensuring device-state heartbeat update occurs

- [ ] **Step 2: Run focused gateway tests to verify failure**

Run:

```powershell
python -m pytest main/xuanwu-iot-gateway/tests/test_dispatch.py main/xuanwu-iot-gateway/tests/test_sensor_ingest.py -q
```

Expected: failures for missing management client methods and missing callback usage.

- [ ] **Step 3: Implement gateway callback integration**

Add to `management_client.py`:
- `post_device_discovery()`
- `post_device_heartbeat()`

Update `gateway_handler.py` to:
- send discovery callback when ingest payload references an unknown/new device context
- send heartbeat/recency updates when commands or ingest are processed
- continue storing local transient state without making it the durable truth

- [ ] **Step 4: Re-run focused gateway tests**

Run:

```powershell
python -m pytest main/xuanwu-iot-gateway/tests/test_dispatch.py main/xuanwu-iot-gateway/tests/test_sensor_ingest.py -q
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add main/xuanwu-iot-gateway/core/clients/management_client.py main/xuanwu-iot-gateway/core/api/gateway_handler.py main/xuanwu-iot-gateway/tests/test_dispatch.py main/xuanwu-iot-gateway/tests/test_sensor_ingest.py
git commit -m "feat: add gateway device discovery callbacks"
```

### Task 4: Add device-server discovery and heartbeat callbacks

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-device-gateway\config\xuanwu_management_client.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-device-gateway\core\api\runtime_handler.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-device-gateway\tests\test_runtime_http_routes.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-device-gateway\tests\test_local_control_plane.py`

- [ ] **Step 1: Write failing device-server tests**

Add tests for:
- runtime-side discovery callback for unknown device first contact
- runtime heartbeat callback after activity
- runtime API route or helper shape required to support callbacks

- [ ] **Step 2: Run focused device-server tests to verify failure**

Run:

```powershell
python -m pytest main/xuanwu-device-gateway/tests/test_runtime_http_routes.py main/xuanwu-device-gateway/tests/test_local_control_plane.py -q
```

Expected: failures for missing callback client methods or missing hook usage.

- [ ] **Step 3: Implement device-server management callbacks**

Add to `xuanwu_management_client.py`:
- `report_device_discovery()`
- `report_device_heartbeat()`

Update runtime-side logic so first-contact and runtime activity can report into management without changing existing runtime config semantics.

- [ ] **Step 4: Re-run focused device-server tests**

Run:

```powershell
python -m pytest main/xuanwu-device-gateway/tests/test_runtime_http_routes.py main/xuanwu-device-gateway/tests/test_local_control_plane.py -q
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add main/xuanwu-device-gateway/config/xuanwu_management_client.py main/xuanwu-device-gateway/core/api/runtime_handler.py main/xuanwu-device-gateway/tests/test_runtime_http_routes.py main/xuanwu-device-gateway/tests/test_local_control_plane.py
git commit -m "feat: add runtime device discovery callbacks"
```

### Task 5: Add portal discovery workspace and promotion flow

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-portal\src\api\management.ts`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-portal\src\pages\DevicesPage.vue`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\main\xuanwu-portal\tests\devices-page.test.ts`

- [ ] **Step 1: Write failing portal tests**

Add tests for:
- loading discovered devices alongside managed devices
- selecting a discovered device
- promoting a discovered device
- ignoring a discovered device
- showing ingress type and discovery status

- [ ] **Step 2: Run focused portal tests to verify failure**

Run:

```powershell
npm test -- --run devices-page.test.ts
```

Expected: failures for missing API client methods and missing UI.

- [ ] **Step 3: Implement portal device workspace enhancements**

Add management API helpers for:
- list/get discovered devices
- promote discovered device
- ignore discovered device

Update `DevicesPage.vue` to:
- show both managed and discovered device sections
- expose provenance fields
- support promote/ignore actions

- [ ] **Step 4: Re-run focused portal tests and build**

Run:

```powershell
npm test -- --run devices-page.test.ts
npm run build
```

Expected: tests and build pass.

- [ ] **Step 5: Commit**

```powershell
git add main/xuanwu-portal/src/api/management.ts main/xuanwu-portal/src/pages/DevicesPage.vue main/xuanwu-portal/tests/devices-page.test.ts
git commit -m "feat: add portal discovered device workflows"
```

### Task 6: Verify, review twice, and update status docs

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\docs\project\state\current.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\docs\project\tasks\2026-03-30-platform-implementation-roadmap.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\device-ingress-integration\docs\superpowers\specs\2026-03-31-spec-completion-status.md`

- [ ] **Step 1: Run full verification**

Run:

```powershell
python -m pytest main/xuanwu-management-server/tests main/xuanwu-iot-gateway/tests main/xuanwu-device-gateway/tests tests/test_xuanwu_portal_docker.py -q
cd main/xuanwu-portal; npm test; npm run build
python -m py_compile main/xuanwu-management-server/app.py main/xuanwu-management-server/core/http_server.py main/xuanwu-management-server/core/api/control_plane_handler.py main/xuanwu-management-server/core/store/local_store.py main/xuanwu-iot-gateway/app.py main/xuanwu-iot-gateway/core/api/gateway_handler.py main/xuanwu-iot-gateway/core/clients/management_client.py main/xuanwu-device-gateway/app.py main/xuanwu-device-gateway/config/xuanwu_management_client.py main/xuanwu-device-gateway/core/api/runtime_handler.py
```

Expected: all pass.

- [ ] **Step 2: Review pass 1**

Review for:
- ingress ownership consistency
- no accidental device truth in gateway/device-server
- no route mismatches

- [ ] **Step 3: Review pass 2**

Review for:
- portal action coverage
- doc alignment
- regression risk around existing runtime resolve and gateway ingest

- [ ] **Step 4: Update status documents**

Mark completion of:
- discovered-device layer
- gateway/device-server ingress integration
- portal device promotion workflow

- [ ] **Step 5: Commit and push**

```powershell
git add docs/project/state/current.md docs/project/tasks/2026-03-30-platform-implementation-roadmap.md docs/superpowers/specs/2026-03-31-spec-completion-status.md
git commit -m "docs: update device ingress integration status"
git push origin codex/device-ingress-integration
```
