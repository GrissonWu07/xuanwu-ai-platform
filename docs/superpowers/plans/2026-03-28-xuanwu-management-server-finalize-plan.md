# XuanWu Management Server Finalize Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove all active `manager-api/web` compatibility logic from `ai-assist-device`, make `xuanwu-management-server` the only management API path, and document any remaining `XuanWu`-side requirements without blocking this repo.

**Architecture:** `main/xuanwu-device-gateway` becomes runtime-only and never reads embedded control-plane or Java management state. `main/xuanwu-management-server` owns all management-side storage and APIs that still need to exist locally, and proxies `Agent` / `Model Provider` / `Model Config` to `XuanWu`. Any upstream gaps are captured in requirements docs rather than reintroducing compatibility code.

**Tech Stack:** Python, aiohttp, pytest, YAML file storage, docker compose.

---

### Task 1: Lock the no-compatibility config boundary

**Files:**
- Modify: `main/xuanwu-device-gateway/config/config_loader.py`
- Modify: `main/xuanwu-device-gateway/config/settings.py`
- Delete: `main/xuanwu-device-gateway/config/manage_api_client.py`
- Modify: `main/xuanwu-device-gateway/tests/test_local_control_plane.py`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run the targeted tests and verify they fail for the removed compatibility paths**
- [ ] **Step 3: Remove manager-api and embedded control-plane fallback from config loading**
- [ ] **Step 4: Run the targeted tests and verify they pass**
- [ ] **Step 5: Commit**

### Task 2: Move report and summary flows to xuanwu-management-server

**Files:**
- Modify: `main/xuanwu-management-server/core/store/local_store.py`
- Modify: `main/xuanwu-management-server/core/api/control_plane_handler.py`
- Modify: `main/xuanwu-management-server/core/http_server.py`
- Modify: `main/xuanwu-device-gateway/config/xuanwu_management_client.py`
- Modify: `main/xuanwu-device-gateway/core/handle/reportHandle.py`
- Modify: `main/xuanwu-device-gateway/core/providers/memory/mem_local_short/mem_local_short.py`
- Modify: `main/xuanwu-management-server/tests/test_local_control_plane.py`
- Modify: `main/xuanwu-management-server/tests/test_http_routes.py`

- [ ] **Step 1: Write failing tests for chat history report and summary-generation requests through xuanwu-management-server**
- [ ] **Step 2: Run the targeted tests and verify they fail**
- [ ] **Step 3: Implement the minimal management-server APIs and device-server client changes**
- [ ] **Step 4: Run the targeted tests and verify they pass**
- [ ] **Step 5: Commit**

### Task 3: Retire remaining legacy control-message and runtime compatibility branches

**Files:**
- Modify: `main/xuanwu-device-gateway/core/connection.py`
- Modify: `main/xuanwu-device-gateway/core/http_server.py`
- Modify: `main/xuanwu-device-gateway/core/handle/textHandler/serverMessageHandler.py`
- Modify: `main/xuanwu-device-gateway/tests/test_runtime_http_routes.py`
- Modify: `main/xuanwu-device-gateway/tests/test_local_control_plane.py`

- [ ] **Step 1: Write failing tests that assert runtime code no longer depends on manager-api compatibility toggles**
- [ ] **Step 2: Run the targeted tests and verify they fail**
- [ ] **Step 3: Remove the gating branches and keep only xuanwu-management-server-driven behavior**
- [ ] **Step 4: Run the targeted tests and verify they pass**
- [ ] **Step 5: Commit**

### Task 4: Remove legacy deployment leftovers and capture XuanWu-side requirements

**Files:**
- Modify: `main/xuanwu-device-gateway/docker-compose_all.yml`
- Modify: `docker-setup.sh`
- Modify: `main/README.md`
- Modify: `main/README_en.md`
- Modify: `docs/Deployment_all.md`
- Modify: `docs/dev-ops-integration.md`
- Add: `docs/superpowers/specs/2026-03-28-xuanwu-upstream-gap-requirements.md`
- Modify: `tests/test_xuanwu_management_server_docs.py`

- [ ] **Step 1: Write failing tests for the final deployment and documentation boundary**
- [ ] **Step 2: Run the targeted tests and verify they fail**
- [ ] **Step 3: Remove default legacy deployment paths and record upstream requirements**
- [ ] **Step 4: Run the targeted tests and verify they pass**
- [ ] **Step 5: Commit**

### Task 5: Verify, review, merge, and push

**Files:**
- Verify only

- [ ] **Step 1: Run the full relevant pytest and py_compile verification suite**
- [ ] **Step 2: Review round 1 against diff, boundary, and regression risks**
- [ ] **Step 3: Fix review findings and rerun impacted verification**
- [ ] **Step 4: Review round 2 against final tree and docs**
- [ ] **Step 5: Merge to `main` and push**
