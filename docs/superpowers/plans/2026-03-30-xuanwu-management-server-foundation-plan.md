# xuanwu-management-server Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 落地 `xuanwu-management-server` 第一阶段基础控制面，使其具备用户、设备、频道、基础映射、runtime resolve 和 `XuanWu` 代理能力。

**Architecture:** 在现有 `main/xuanwu-management-server` 骨架上扩展本地 store、API handler 和 HTTP 路由，先以文件落盘作为真源，保持 `Agent` 域对象继续代理到 `XuanWu`。所有新能力都围绕“本地设备治理真源 + 上游 Agent 域代理”展开。

**Tech Stack:** Python 3, existing `xuanwu-management-server` HTTP server, file-backed local store, pytest

---

### Task 1: 扩展本地 store 的用户、频道和映射真源

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\core\store\local_store.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\core\store\exceptions.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\tests\test_local_control_plane.py`

- [ ] **Step 1: Write the failing test**

```python
def test_store_creates_user_channel_and_device_mappings(store):
    user = store.create_user({"user_id": "user-001", "name": "Alice"})
    channel = store.create_channel({"channel_id": "channel-home", "user_id": "user-001", "name": "Home"})
    mapping = store.bind_device_agent({
        "mapping_id": "map-device-agent-001",
        "device_id": "dev-001",
        "agent_id": "agent-frontdesk",
    })

    assert user["user_id"] == "user-001"
    assert channel["channel_id"] == "channel-home"
    assert mapping["agent_id"] == "agent-frontdesk"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py -k user_channel -v`
Expected: FAIL with missing `create_user` / `create_channel` / `bind_device_agent`

- [ ] **Step 3: Write minimal implementation**

```python
def create_user(self, payload: dict) -> dict:
    return self._upsert_yaml("users", payload["user_id"], payload)

def create_channel(self, payload: dict) -> dict:
    return self._upsert_yaml("channels", payload["channel_id"], payload)

def bind_device_agent(self, payload: dict) -> dict:
    return self._upsert_yaml("device_agent_mappings", payload["mapping_id"], payload)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py -k user_channel -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-management-server/core/store/local_store.py main/xuanwu-management-server/core/store/exceptions.py main/xuanwu-management-server/tests/test_local_control_plane.py
git commit -m "feat: add management store mappings"
```

### Task 2: 为用户、设备、频道和映射新增管理 API

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\core\api\control_plane_handler.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\core\http_server.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\tests\test_http_routes.py`

- [ ] **Step 1: Write the failing test**

```python
def test_http_routes_support_user_and_channel_crud(client):
    response = client.post("/control-plane/v1/users", json={"user_id": "user-001", "name": "Alice"})
    assert response.status_code == 201

    response = client.post("/control-plane/v1/channels", json={"channel_id": "channel-home", "user_id": "user-001", "name": "Home"})
    assert response.status_code == 201
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest main/xuanwu-management-server/tests/test_http_routes.py -k user_and_channel -v`
Expected: FAIL because routes do not exist

- [ ] **Step 3: Write minimal implementation**

```python
if method == "POST" and path == "/control-plane/v1/users":
    return self._json_response(self._store.create_user(body), status=201)

if method == "POST" and path == "/control-plane/v1/channels":
    return self._json_response(self._store.create_channel(body), status=201)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest main/xuanwu-management-server/tests/test_http_routes.py -k user_and_channel -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-management-server/core/api/control_plane_handler.py main/xuanwu-management-server/core/http_server.py main/xuanwu-management-server/tests/test_http_routes.py
git commit -m "feat: add management api routes for users and channels"
```

### Task 3: 落地 runtime resolve 与绑定视图

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\core\store\local_store.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\core\api\control_plane_handler.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\tests\test_local_control_plane.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\tests\test_http_routes.py`

- [ ] **Step 1: Write the failing test**

```python
def test_runtime_resolve_returns_user_device_agent_binding(client):
    response = client.post("/control-plane/v1/runtime/device-config:resolve", json={
        "device_id": "dev-001",
        "client_id": "client-001",
    })

    body = response.json()
    assert body["device_id"] == "dev-001"
    assert body["binding"]["agent_id"] == "agent-frontdesk"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest main/xuanwu-management-server/tests/test_http_routes.py -k runtime_resolve -v`
Expected: FAIL because binding view is incomplete

- [ ] **Step 3: Write minimal implementation**

```python
def resolve_runtime_binding(self, device_id: str, client_id: str | None = None) -> dict:
    device = self.get_device(device_id)
    agent_mapping = self.get_active_device_agent_mapping(device_id)
    return {
        "device_id": device_id,
        "client_id": client_id,
        "binding": agent_mapping,
        "runtime_overrides": device.get("runtime_overrides", {}),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py -k runtime_resolve -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-management-server/core/store/local_store.py main/xuanwu-management-server/core/api/control_plane_handler.py main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py
git commit -m "feat: add runtime binding resolve view"
```

### Task 4: 稳定 `XuanWu` 代理入口

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\core\clients\xuanwu_client.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\core\api\xuanwu_proxy_handler.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\tests\test_xuanwu_proxy_contract.py`

- [ ] **Step 1: Write the failing test**

```python
def test_xuanwu_proxy_maps_upstream_conflict(fake_xuanwu):
    fake_xuanwu.conflict_on("POST", "/xuanwu/v1/admin/agents")
    response = fake_xuanwu.client.post("/control-plane/v1/xuanwu/agents", json={"agent_id": "agent-frontdesk"})
    assert response.status_code == 409
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest main/xuanwu-management-server/tests/test_xuanwu_proxy_contract.py -k conflict -v`
Expected: FAIL because error mapping is not stable enough

- [ ] **Step 3: Write minimal implementation**

```python
if upstream_status == 409:
    return self._json_error("resource_conflict", upstream_body, status=409)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest main/xuanwu-management-server/tests/test_xuanwu_proxy_contract.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-management-server/core/clients/xuanwu_client.py main/xuanwu-management-server/core/api/xuanwu_proxy_handler.py main/xuanwu-management-server/tests/test_xuanwu_proxy_contract.py
git commit -m "feat: stabilize xuanwu proxy contract"
```

### Task 5: 完成阶段验收与文档同步

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\docs\project\state\current.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\docs\project\tasks\2026-03-30-platform-implementation-roadmap.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-management-server\README.md`

- [ ] **Step 1: Run target tests**

Run: `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-management-server/tests/test_xuanwu_proxy_contract.py -q`
Expected: PASS

- [ ] **Step 2: Run syntax validation**

Run: `python -m py_compile main/xuanwu-management-server/app.py main/xuanwu-management-server/core/http_server.py main/xuanwu-management-server/core/api/control_plane_handler.py main/xuanwu-management-server/core/api/xuanwu_proxy_handler.py main/xuanwu-management-server/core/store/local_store.py`
Expected: PASS

- [ ] **Step 3: Update state and roadmap**

```markdown
## Completed
- xuanwu-management-server phase 1 foundation completed

## Next Step
- telemetry / event / gateway / ota governance
```

- [ ] **Step 4: Update README**

```markdown
## Current Scope
- users
- devices
- channels
- mappings
- runtime resolve
- xuanwu proxy
```

- [ ] **Step 5: Commit**

```bash
git add docs/project/state/current.md docs/project/tasks/2026-03-30-platform-implementation-roadmap.md main/xuanwu-management-server/README.md
git commit -m "docs: record management server phase 1 completion"
```

## Verification
- command: `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-management-server/tests/test_xuanwu_proxy_contract.py -q`
- expected: 所有阶段一测试通过
- actual: 待执行
- command: `python -m py_compile main/xuanwu-management-server/app.py main/xuanwu-management-server/core/http_server.py main/xuanwu-management-server/core/api/control_plane_handler.py main/xuanwu-management-server/core/api/xuanwu_proxy_handler.py main/xuanwu-management-server/core/store/local_store.py`
- expected: 语法校验通过
- actual: 待执行

## Handoff Notes
- 本计划只覆盖 `xuanwu-management-server` 第一阶段基础控制面
- `xuanwu-gateway`、事件遥测治理、`xuanwu-device-server` 边界收口应进入后续独立计划
- `XuanWu` 仍按契约集成，不在本计划中实现其真源逻辑
