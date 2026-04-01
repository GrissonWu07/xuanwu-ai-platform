# Xuanwu Management Server Bootstrap Implementation Plan

> Historical execution record: the original `XuanWu` proxy contract tests referenced below were removed from the active local verification gate because upstream `XuanWu` is not integrated yet. Treat those references as archived context, not current completion criteria.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `main/xuanwu-management-server`, move embedded control-plane ownership out of `main/xuanwu-device-gateway`, and prepare the first replacement path for legacy `manager-api/web`.

**Architecture:** Start by extracting the existing embedded control-plane code into a standalone Python service with the same behavior and tests. Then rewire `xuanwu-device-gateway` to runtime-only responsibilities and build forward from the new management host.

**Tech Stack:** Python, aiohttp, unittest/pytest, existing local control-plane store, existing runtime/config modules

---

### Task 1: Create `main/xuanwu-management-server` Skeleton

**Files:**
- Create: `main/xuanwu-management-server/app.py`
- Create: `main/xuanwu-management-server/config/__init__.py`
- Create: `main/xuanwu-management-server/config/logger.py`
- Create: `main/xuanwu-management-server/core/__init__.py`
- Create: `main/xuanwu-management-server/core/http_server.py`
- Create: `main/xuanwu-management-server/tests/test_bootstrap.py`

- [ ] **Step 1: Write the failing bootstrap test**
- [ ] **Step 2: Run the bootstrap test to confirm import/startup failure**
- [ ] **Step 3: Add the minimal service skeleton to satisfy the test**
- [ ] **Step 4: Re-run the bootstrap test and confirm it passes**

### Task 2: Extract Embedded Control-Plane Code

**Files:**
- Create: `main/xuanwu-management-server/core/api/control_plane_handler.py`
- Create: `main/xuanwu-management-server/core/store/local_store.py`
- Create: `main/xuanwu-management-server/core/store/import_bundle.py`
- Create: `main/xuanwu-management-server/core/store/exceptions.py`
- Create: `main/xuanwu-management-server/tests/test_local_control_plane.py`
- Modify: `main/xuanwu-device-gateway/core/api/control_plane_handler.py`
- Modify: `main/xuanwu-device-gateway/core/control_plane/local_store.py`
- Modify: `main/xuanwu-device-gateway/core/control_plane/import_bundle.py`
- Modify: `main/xuanwu-device-gateway/core/control_plane/exceptions.py`

- [ ] **Step 1: Copy the current control-plane tests into the new service and adapt imports**
- [ ] **Step 2: Run the new service tests to verify they fail because modules do not exist**
- [ ] **Step 3: Move the minimal control-plane modules into `xuanwu-management-server`**
- [ ] **Step 4: Re-run the extracted control-plane tests and confirm they pass**

### Task 3: Move HTTP Routing Ownership

**Files:**
- Modify: `main/xuanwu-management-server/core/http_server.py`
- Modify: `main/xuanwu-management-server/app.py`
- Modify: `main/xuanwu-device-gateway/core/http_server.py`
- Create: `main/xuanwu-management-server/tests/test_http_routes.py`

- [ ] **Step 1: Write a failing route test asserting `xuanwu-management-server` exposes `/control-plane/v1/*`**
- [ ] **Step 2: Run the route test and verify it fails for the intended missing-route reason**
- [ ] **Step 3: Add the extracted HTTP routing to `xuanwu-management-server`**
- [ ] **Step 4: Remove `/control-plane/v1/*` route registration from `xuanwu-device-gateway`**
- [ ] **Step 5: Re-run route tests and existing runtime tests to confirm the split passes**

### Task 4: Rewire Tests and Imports Around the New Host

**Files:**
- Modify: `main/xuanwu-device-gateway/tests/test_local_control_plane.py`
- Modify: `main/xuanwu-management-server/tests/test_local_control_plane.py`
- Modify: `main/xuanwu-device-gateway/app.py`
- Modify: `main/xuanwu-device-gateway/config/config_loader.py`

- [ ] **Step 1: Add a failing test that `xuanwu-device-gateway` no longer exposes management routes**
- [ ] **Step 2: Run that test and confirm it fails before final cleanup**
- [ ] **Step 3: Update imports/config wiring to point management ownership at `xuanwu-management-server`**
- [ ] **Step 4: Re-run both service test suites and confirm the boundary is green**

### Task 5: Add First `XuanWu` Proxy Contract Stubs

**Files:**
- Create: `main/xuanwu-management-server/core/api/xuanwu_proxy_handler.py`
- Create: `main/xuanwu-management-server/core/clients/xuanwu_client.py`
- Modify: `main/xuanwu-management-server/core/http_server.py`

- [ ] **Step 1: Write failing proxy contract tests for agents/providers/models pass-through routes**
- [ ] **Step 2: Run the proxy tests and confirm they fail because handlers do not exist**
- [ ] **Step 3: Implement minimal proxy handlers and client wiring with headers and error mapping**
- [ ] **Step 4: Re-run proxy tests and confirm the pass-through contract is green**
- [ ] **Step 4: Re-run proxy tests and confirm the pass-through contract is green**
  - Historical note: the original local proxy contract test file was later retired from the local-only gate and replaced by upstream contract tracking.

### Task 6: Verification and Review

**Files:**
- Modify: `docs/superpowers/specs/2026-03-28-xuanwu-management-server-replacement-design.md`
- Modify: `docs/superpowers/plans/2026-03-28-xuanwu-management-server-bootstrap-plan.md`

- [ ] **Step 1: Run targeted verification**
  - `python -m pytest main/xuanwu-management-server/tests -q`
  - `python -m pytest main/xuanwu-device-gateway/tests/test_local_control_plane.py -q`
- [ ] **Step 2: Run broader syntax verification**
  - `python -m py_compile main/xuanwu-management-server/app.py main/xuanwu-management-server/core/http_server.py main/xuanwu-device-gateway/core/http_server.py`
- [ ] **Step 3: Review pass 1**
  - confirm `xuanwu-device-gateway` no longer owns `/control-plane/v1/*`
  - confirm `xuanwu-management-server` is the only management host
- [ ] **Step 4: Review pass 2**
  - confirm `XuanWu` proxy contract headers and error mapping are present
  - confirm no local source-of-truth was added for `Agent`, `Model Provider`, or `Model Config`
