# xuanwu-jobs Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first Docker-ready `xuanwu-jobs` service with Redis-backed queueing and horizontally scalable platform workers.

**Architecture:** Add a dedicated async Python jobs service that polls due schedules from `xuanwu-management-server`, enqueues jobs to Redis through ARQ, and runs local platform jobs in separate worker processes. Keep schedule truth in `xuanwu-management-server`, and keep `XuanWu`/gateway execution out of this repository.

**Tech Stack:** Python 3, aiohttp, ARQ, Redis, pytest

---

### Task 1: Create `xuanwu-jobs` service skeleton

**Files:**
- Create: `main/xuanwu-jobs/app.py`
- Create: `main/xuanwu-jobs/README.md`
- Create: `main/xuanwu-jobs/core/__init__.py`
- Create: `main/xuanwu-jobs/core/http_server.py`
- Create: `main/xuanwu-jobs/tests/test_xuanwu_jobs_bootstrap.py`

- [x] **Step 1: Write the failing bootstrap test**
- [x] **Step 2: Run the bootstrap test and confirm missing module failure**
- [x] **Step 3: Implement minimal aiohttp app with health route**
- [x] **Step 4: Re-run bootstrap test and confirm it passes**

### Task 2: Add queue config, scheduler contract, and platform worker contract

**Files:**
- Create: `main/xuanwu-jobs/config/__init__.py`
- Create: `main/xuanwu-jobs/config/settings.py`
- Create: `main/xuanwu-jobs/core/queue.py`
- Create: `main/xuanwu-jobs/core/scheduler.py`
- Create: `main/xuanwu-jobs/core/platform_worker.py`
- Create: `main/xuanwu-jobs/tests/test_scheduler_contract.py`
- Create: `main/xuanwu-jobs/tests/test_platform_worker.py`

- [x] **Step 1: Write failing scheduler and worker tests with realistic schedule payloads**
- [x] **Step 2: Run tests to confirm contract failures**
- [x] **Step 3: Implement minimal queue names and scheduler/worker entry contracts**
- [x] **Step 4: Re-run tests and confirm they pass**

### Task 3: Add management-side due-schedule and job-run APIs

**Files:**
- Modify: `main/xuanwu-management-server/core/store/local_store.py`
- Modify: `main/xuanwu-management-server/core/api/control_plane_handler.py`
- Modify: `main/xuanwu-management-server/core/http_server.py`
- Modify: `main/xuanwu-management-server/tests/test_local_control_plane.py`
- Modify: `main/xuanwu-management-server/tests/test_http_routes.py`

- [x] **Step 1: Write failing management tests for due schedules, claim, and run status**
- [x] **Step 2: Run tests to confirm routes and store methods are missing**
- [x] **Step 3: Implement minimal local schedule truth and run-status endpoints**
- [x] **Step 4: Re-run management tests and confirm they pass**

### Task 4: Wire scheduler polling and worker execution

**Files:**
- Modify: `main/xuanwu-jobs/core/scheduler.py`
- Modify: `main/xuanwu-jobs/core/platform_worker.py`
- Create: `main/xuanwu-jobs/core/clients/management_client.py`
- Create: `main/xuanwu-jobs/tests/test_end_to_end_jobs.py`

- [x] **Step 1: Write failing end-to-end test for due schedule -> queue -> completion path**
- [x] **Step 2: Run test to confirm the scheduler/worker path fails**
- [x] **Step 3: Implement polling, claim, enqueue, and completion reporting**
- [x] **Step 4: Re-run end-to-end test and confirm it passes**

### Task 5: Add Docker Compose support for horizontal worker scaling

**Files:**
- Modify: `main/xuanwu-device-server/docker-compose_all.yml`
- Modify: `docker-setup.sh`
- Modify: `main/xuanwu-management-server/README.md`
- Modify: `main/xuanwu-jobs/README.md`
- Modify: `main/README.md`
- Modify: `main/README_en.md`

- [x] **Step 1: Write a failing repo/documentation test that expects Redis and jobs services**
- [x] **Step 2: Run the test and confirm the current compose/doc setup fails**
- [x] **Step 3: Add Redis, scheduler, and platform-worker services plus scale instructions**
- [x] **Step 4: Re-run the test and confirm Docker documentation and compose are aligned**

### Task 6: Update state and verify

**Files:**
- Modify: `docs/project/state/current.md`
- Modify: `docs/project/tasks/2026-03-30-platform-implementation-roadmap.md`
- Modify: `docs/superpowers/specs/README.md`

- [x] **Step 1: Run target tests**
  - `python -m pytest main/xuanwu-jobs/tests/test_xuanwu_jobs_bootstrap.py main/xuanwu-jobs/tests/test_scheduler_contract.py main/xuanwu-jobs/tests/test_platform_worker.py main/xuanwu-jobs/tests/test_end_to_end_jobs.py main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py -q`
- [ ] **Step 2: Run broader verification**
  - `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-gateway/tests/test_bootstrap.py main/xuanwu-gateway/tests/test_registry.py main/xuanwu-gateway/tests/test_dispatch.py main/xuanwu-device-server/tests/test_local_control_plane.py main/xuanwu-device-server/tests/test_runtime_http_routes.py main/xuanwu-device-server/tests/test_runtime_handler_unit.py main/xuanwu-jobs/tests/test_xuanwu_jobs_bootstrap.py main/xuanwu-jobs/tests/test_scheduler_contract.py main/xuanwu-jobs/tests/test_platform_worker.py main/xuanwu-jobs/tests/test_end_to_end_jobs.py tests/test_active_spec_index.py -q`
- [ ] **Step 3: Run syntax validation**
  - `python -m py_compile main/xuanwu-jobs/app.py main/xuanwu-jobs/core/http_server.py main/xuanwu-jobs/core/scheduler.py main/xuanwu-jobs/core/platform_worker.py main/xuanwu-jobs/core/clients/management_client.py`
- [x] **Step 4: Update state and spec index**
- [ ] **Step 5: Commit**
