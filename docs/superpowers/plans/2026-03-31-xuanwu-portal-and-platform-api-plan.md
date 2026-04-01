# xuanwu-portal and Platform API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `main/xuanwu-portal` as the single Vue 3 frontend entry and complete the local platform APIs required for its first delivery.

**Architecture:** The work is split into two parallel tracks. Track A builds the new `xuanwu-portal` Vue 3 application and Phase 1 pages. Track B extends `xuanwu-management-server` with portal-facing read models and shell/session APIs. The frontend consumes local platform APIs by domain and degrades gracefully where `XuanWu` upstream integration is not yet live.

**Tech Stack:** Vue 3, TypeScript, Vite, Vue Router, Pinia, aiohttp, pytest

---

## File Structure

### Frontend Track

- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\package.json`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\vite.config.ts`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\tsconfig.json`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\index.html`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\main.ts`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\App.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\router\index.ts`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\stores\*.ts`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\components\shell\*.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\components\ui\*.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\pages\OverviewPage.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\pages\DevicesPage.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\pages\AgentsPage.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\pages\JobsPage.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\pages\AlertsPage.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\api\*.ts`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\styles\*.css`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\tests\*.test.ts`

### Backend Track

- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\http_server.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\api\control_plane_handler.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\store\local_store.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_local_control_plane.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_http_routes.py`
- Optional Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-iot-gateway\core\http_server.py`
- Optional Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-iot-gateway\core\api\gateway_handler.py`

## Parallel Track A: xuanwu-portal

### Task 1: Bootstrap the Vue 3 application

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\package.json`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\vite.config.ts`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\tsconfig.json`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\main.ts`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\tests\bootstrap.test.ts`

- [ ] Write a failing bootstrap test that asserts the app shell can mount and exposes the primary five tabs.
- [ ] Run the bootstrap test and confirm it fails because the app does not exist yet.
- [ ] Create the minimal Vite + Vue 3 app structure and mount the root application.
- [ ] Run the bootstrap test again and confirm it passes.
- [ ] Commit the bootstrap slice.

### Task 2: Build the unified shell

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\App.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\components\shell\PortalShell.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\components\shell\ProfileMenu.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\components\shell\PrimaryTabs.vue`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\tests\shell.test.ts`

- [ ] Write a failing shell test that verifies there is no left sidebar and that the shell renders centered tabs plus a top-right profile menu.
- [ ] Run the shell test and verify the failure is real.
- [ ] Implement the shell and align the layout to the approved `xuanwu-portal` concept.
- [ ] Run the shell test and confirm it passes.
- [ ] Commit the shell slice.

### Task 3: Implement Overview

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\pages\OverviewPage.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\api\management.ts`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\tests\overview.test.ts`

- [ ] Write a failing test for the Overview page using a realistic dashboard payload.
- [ ] Run the failing test.
- [ ] Implement the Overview page against `GET /control-plane/v1/dashboard/overview`.
- [ ] Run the page test and confirm it passes.
- [ ] Commit the Overview slice.

### Task 4: Implement Devices

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\pages\DevicesPage.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\components\ui\DataTable.vue`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\tests\devices.test.ts`

- [ ] Write a failing test that renders a realistic devices collection and detail payload.
- [ ] Run the failing test.
- [ ] Implement the Devices page using `/control-plane/v1/devices` and `/control-plane/v1/devices/{device_id}/detail`.
- [ ] Run the page test and confirm it passes.
- [ ] Commit the Devices slice.

### Task 5: Implement Jobs and Alerts

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\pages\JobsPage.vue`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\pages\AlertsPage.vue`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\tests\jobs.test.ts`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\tests\alerts.test.ts`

- [ ] Write failing tests using realistic schedule, job run, and alert payloads.
- [ ] Run those tests to verify the failures.
- [ ] Implement `JobsPage` against `/control-plane/v1/jobs/overview` and existing jobs endpoints.
- [ ] Implement `AlertsPage` against `/control-plane/v1/alerts/overview`, `/control-plane/v1/alarms`, and ack endpoints.
- [ ] Run the tests and confirm they pass.
- [ ] Commit the Jobs and Alerts slice.

### Task 6: Implement Agents with graceful upstream fallback

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\src\pages\AgentsPage.vue`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-portal\tests\agents.test.ts`

- [ ] Write a failing test for live proxy success and upstream-unavailable fallback.
- [ ] Run the failing test.
- [ ] Implement the Agents page against `/control-plane/v1/xuanwu/agents`, `/model-providers`, and `/models`.
- [ ] Ensure upstream failure is rendered as a real empty/unavailable state instead of a crash.
- [ ] Run the tests and confirm they pass.
- [ ] Commit the Agents slice.

## Parallel Track B: Platform API completion

### Task 7: Add profile/session read APIs

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\http_server.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\api\control_plane_handler.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\store\local_store.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_local_control_plane.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_http_routes.py`

- [ ] Write failing tests for `GET /control-plane/v1/auth/me` and `GET /control-plane/v1/roles` using realistic user and role payloads.
- [ ] Run the target tests and verify they fail.
- [ ] Implement both endpoints in handler, store, and route registration.
- [ ] Re-run the target tests and confirm they pass.
- [ ] Commit the profile/session slice.

### Task 8: Add dashboard and portal shell APIs

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\http_server.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\api\control_plane_handler.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\store\local_store.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_local_control_plane.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_http_routes.py`

- [ ] Write failing tests for `GET /control-plane/v1/dashboard/overview` and `GET /control-plane/v1/portal/config`.
- [ ] Run the target tests and verify the failure.
- [ ] Implement dashboard aggregation and portal config responses with realistic summary sections.
- [ ] Re-run the tests and confirm they pass.
- [ ] Commit the dashboard/config slice.

### Task 9: Add jobs and alerts read models

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\http_server.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\api\control_plane_handler.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\store\local_store.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_local_control_plane.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_http_routes.py`

- [ ] Write failing tests for `GET /control-plane/v1/jobs/overview`, `GET /control-plane/v1/jobs/runs/{job_run_id}`, `GET /control-plane/v1/alarms/{alarm_id}`, and `GET /control-plane/v1/alerts/overview`.
- [ ] Run the tests and verify the failures.
- [ ] Implement the read-model endpoints.
- [ ] Re-run the tests and confirm they pass.
- [ ] Commit the jobs/alerts slice.

### Task 10: Add device detail read model

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\http_server.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\api\control_plane_handler.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\store\local_store.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_local_control_plane.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_http_routes.py`

- [ ] Write a failing test for `GET /control-plane/v1/devices/{device_id}/detail` using realistic nested device, owner, mapping, runtime, event, and telemetry data.
- [ ] Run the test and confirm it fails.
- [ ] Implement the detail read model.
- [ ] Re-run the test and confirm it passes.
- [ ] Commit the device detail slice.

### Task 11: Add gateway overview aggregation if still needed

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\http_server.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\api\control_plane_handler.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\store\local_store.py`
- Optional Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-iot-gateway\core\api\gateway_handler.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_local_control_plane.py`

- [ ] Decide whether `Overview` can stay frontend-composed without a dedicated gateway overview. If not, write a failing test for `GET /control-plane/v1/gateway/overview`.
- [ ] Implement the smallest useful overview shape only if the test proves it is needed.
- [ ] Re-run the tests and confirm they pass.
- [ ] Commit only if the endpoint adds real frontend value.

## Integration and Review

### Task 12: Spec compliance review

**Files:**
- Review all frontend changes against `2026-03-31-xuanwu-portal-frontend-spec.md`
- Review all backend changes against `2026-03-31-platform-api-completion-spec.md`

- [ ] Review the frontend branch against the frontend spec and list any missing page or shell requirement.
- [ ] Review the backend branch against the API completion spec and list any missing endpoint or response shape.
- [ ] Fix gaps before code-quality review begins.

### Task 13: Code quality review

**Files:**
- Review changed files in both tracks

- [ ] Review for oversized files, duplicated API client logic, weak error states, and low-signal tests.
- [ ] Fix quality issues.
- [ ] Re-run the relevant tests.

### Task 14: Final validation

**Files:**
- All modified frontend and backend files

- [ ] Run backend tests:
  - `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py -q`
- [ ] Run frontend tests:
  - project-appropriate test command inside `main/xuanwu-portal`
- [ ] Run build verification for the frontend:
  - project-appropriate build command inside `main/xuanwu-portal`
- [ ] If possible, run a local smoke check to confirm the portal shell can render with live local APIs.
- [ ] Commit final integration fixes.
