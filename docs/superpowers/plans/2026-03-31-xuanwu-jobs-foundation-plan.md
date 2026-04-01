# xuanwu-jobs Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first Docker-ready `xuanwu-jobs` service as a lightweight scheduler-dispatcher without a separate jobs-worker deployment.

**Architecture:** Add a dedicated async Python jobs service that polls due schedules from `xuanwu-management-server`, claims them, and dispatches them directly to local service execution APIs. Keep schedule truth in `xuanwu-management-server`, keep actual execution inside `xuanwu-management-server` / `xuanwu-iot-gateway` / `xuanwu-device-gateway`, and leave `XuanWu` execution as an upstream contract.

**Tech Stack:** Python 3, aiohttp, httpx, pytest

---

### Task 1: Keep `xuanwu-jobs` bootstrap minimal

**Files:**
- Modify: `main/xuanwu-jobs/app.py`
- Modify: `main/xuanwu-jobs/core/http_server.py`
- Modify: `main/xuanwu-jobs/core/api/jobs_handler.py`
- Modify: `main/xuanwu-jobs/tests/test_xuanwu_jobs_bootstrap.py`

- [ ] **Step 1: Write the failing bootstrap/config tests**
- [ ] **Step 2: Run the bootstrap tests and confirm the current config shape fails**
- [ ] **Step 3: Implement minimal aiohttp app with direct-dispatch config surface**
- [ ] **Step 4: Re-run bootstrap tests and confirm they pass**

### Task 2: Replace queue/worker semantics with scheduler-dispatch contracts

**Files:**
- Modify: `main/xuanwu-jobs/config/settings.py`
- Create: `main/xuanwu-jobs/core/dispatcher.py`
- Modify: `main/xuanwu-jobs/core/scheduler.py`
- Create: `main/xuanwu-jobs/core/clients/gateway_client.py`
- Create: `main/xuanwu-jobs/core/clients/device_client.py`
- Modify: `main/xuanwu-jobs/core/clients/management_client.py`
- Create: `main/xuanwu-jobs/tests/test_dispatcher_contract.py`
- Modify: `main/xuanwu-jobs/tests/test_scheduler_contract.py`

- [ ] **Step 1: Write failing scheduler/dispatcher tests with realistic claimed-job payloads**
- [ ] **Step 2: Run tests to confirm current queue/worker semantics fail**
- [ ] **Step 3: Implement minimal dispatch target config and scheduler/dispatcher contracts**
- [ ] **Step 4: Re-run tests and confirm they pass**

### Task 3: Add local execution endpoints in management, gateway, and device services

**Files:**
- Modify: `main/xuanwu-management-server/core/api/control_plane_handler.py`
- Modify: `main/xuanwu-management-server/core/http_server.py`
- Modify: `main/xuanwu-management-server/tests/test_http_routes.py`
- Modify: `main/xuanwu-iot-gateway/core/api/gateway_handler.py`
- Modify: `main/xuanwu-iot-gateway/core/http_server.py`
- Modify: `main/xuanwu-iot-gateway/tests/test_dispatch.py`
- Modify: `main/xuanwu-device-gateway/core/api/runtime_handler.py`
- Modify: `main/xuanwu-device-gateway/core/http_server.py`
- Modify: `main/xuanwu-device-gateway/tests/test_runtime_handler_unit.py`

- [ ] **Step 1: Write failing execution-endpoint tests for `platform`, `gateway`, and `device` dispatch**
- [ ] **Step 2: Run the tests and confirm the endpoints are missing**
- [ ] **Step 3: Implement minimal local execution APIs with realistic payload validation**
- [ ] **Step 4: Re-run the service tests and confirm they pass**

### Task 4: Wire scheduler polling and direct dispatch execution

**Files:**
- Modify: `main/xuanwu-jobs/core/scheduler.py`
- Modify: `main/xuanwu-jobs/core/dispatcher.py`
- Modify: `main/xuanwu-jobs/tests/test_end_to_end_jobs.py`

- [ ] **Step 1: Write failing end-to-end test for due schedule -> claim -> dispatch -> completion**
- [ ] **Step 2: Run the test and confirm the dispatch path fails**
- [ ] **Step 3: Implement polling, claim, dispatch, and completion reporting**
- [ ] **Step 4: Re-run the end-to-end test and confirm it passes**

### Task 5: Simplify Docker and docs to a single `xuanwu-jobs` service

**Files:**
- Modify: `main/xuanwu-device-gateway/docker-compose_all.yml`
- Modify: `docker-setup.sh`
- Modify: `main/xuanwu-jobs/README.md`
- Modify: `main/README.md`
- Modify: `main/README_en.md`
- Modify: `tests/test_xuanwu_jobs_docker.py`

- [ ] **Step 1: Write a failing repo/documentation test that expects one `xuanwu-jobs` service without Redis/jobs-worker**
- [ ] **Step 2: Run the test and confirm the current compose/doc setup fails**
- [ ] **Step 3: Simplify compose and installation docs to a single `xuanwu-jobs` service**
- [ ] **Step 4: Re-run the test and confirm Docker documentation and compose are aligned**

### Task 6: Update state and verify

**Files:**
- Modify: `docs/project/state/current.md`
- Modify: `docs/project/tasks/2026-03-30-platform-implementation-roadmap.md`
- Modify: `docs/superpowers/specs/README.md`

- [ ] **Step 1: Run target tests**
  - `python -m pytest main/xuanwu-jobs/tests/test_xuanwu_jobs_bootstrap.py main/xuanwu-jobs/tests/test_scheduler_contract.py main/xuanwu-jobs/tests/test_scheduler_routing.py main/xuanwu-jobs/tests/test_dispatcher_contract.py main/xuanwu-jobs/tests/test_end_to_end_jobs.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-iot-gateway/tests/test_bootstrap.py main/xuanwu-iot-gateway/tests/test_dispatch.py main/xuanwu-device-gateway/tests/test_runtime_http_routes.py main/xuanwu-device-gateway/tests/test_runtime_handler_unit.py tests/test_xuanwu_jobs_docker.py -q`
- [ ] **Step 2: Run broader verification**
  - `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-iot-gateway/tests/test_bootstrap.py main/xuanwu-iot-gateway/tests/test_registry.py main/xuanwu-iot-gateway/tests/test_dispatch.py main/xuanwu-device-gateway/tests/test_local_control_plane.py main/xuanwu-device-gateway/tests/test_runtime_http_routes.py main/xuanwu-device-gateway/tests/test_runtime_handler_unit.py main/xuanwu-jobs/tests/test_xuanwu_jobs_bootstrap.py main/xuanwu-jobs/tests/test_scheduler_contract.py main/xuanwu-jobs/tests/test_scheduler_routing.py main/xuanwu-jobs/tests/test_dispatcher_contract.py main/xuanwu-jobs/tests/test_end_to_end_jobs.py tests/test_active_spec_index.py tests/test_xuanwu_jobs_docker.py -q`
- [ ] **Step 3: Run syntax validation**
  - `python -m py_compile main/xuanwu-jobs/app.py main/xuanwu-jobs/core/http_server.py main/xuanwu-jobs/core/scheduler.py main/xuanwu-jobs/core/dispatcher.py main/xuanwu-jobs/core/clients/management_client.py main/xuanwu-jobs/core/clients/gateway_client.py main/xuanwu-jobs/core/clients/device_client.py`
- [ ] **Step 4: Update state and spec index**
- [ ] **Step 5: Commit**
