# xuanwu-gateway Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 落地独立的 `xuanwu-gateway` 基础模块、统一命令合同、adapter registry 和首批 `http` / `mqtt` / `home_assistant` 适配器。

**Architecture:** 使用与 `xuanwu-management-server` 一致的 Python + aiohttp 宿主模式，先以稳定合同和 dry-run adapter 为主，确保命令能按 `adapter_type` 路由和回包，再为后续真实协议接入预留边界。

**Tech Stack:** Python 3, aiohttp, pytest

---

### Task 1: 创建 `xuanwu-gateway` 模块骨架

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\app.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\core\http_server.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\README.md`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\tests\test_bootstrap.py`

- [ ] **Step 1: Write the failing test**

```python
def test_create_app_registers_gateway_routes():
    app = create_app({})
    registered_paths = sorted(
        route.resource.canonical for route in app.router.routes() if hasattr(route.resource, "canonical")
    )
    assert "/gateway/v1/adapters" in registered_paths
    assert "/gateway/v1/commands:dispatch" in registered_paths
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest main/xuanwu-gateway/tests/test_bootstrap.py -v`
Expected: FAIL because module and routes do not exist

- [ ] **Step 3: Write minimal implementation**

```python
def create_http_app(config: dict) -> web.Application:
    app = web.Application()
    app.add_routes([...])
    return app
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest main/xuanwu-gateway/tests/test_bootstrap.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-gateway/app.py main/xuanwu-gateway/core/http_server.py main/xuanwu-gateway/README.md main/xuanwu-gateway/tests/test_bootstrap.py
git commit -m "feat: bootstrap xuanwu gateway service"
```

### Task 2: 落地 adapter registry 与合同模型

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\core\registry\adapter_registry.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\core\contracts\models.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\core\adapters\base.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\tests\test_registry.py`

- [ ] **Step 1: Write the failing test**

```python
def test_registry_lists_builtin_adapters():
    registry = create_builtin_registry()
    adapter_types = sorted(item["adapter_type"] for item in registry.describe())
    assert adapter_types == ["home_assistant", "http", "mqtt"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest main/xuanwu-gateway/tests/test_registry.py -v`
Expected: FAIL because registry does not exist

- [ ] **Step 3: Write minimal implementation**

```python
class AdapterRegistry:
    def register(self, adapter): ...
    def get(self, adapter_type): ...
    def describe(self): ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest main/xuanwu-gateway/tests/test_registry.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-gateway/core/registry/adapter_registry.py main/xuanwu-gateway/core/contracts/models.py main/xuanwu-gateway/core/adapters/base.py main/xuanwu-gateway/tests/test_registry.py
git commit -m "feat: add gateway adapter registry"
```

### Task 3: 实现首批 dry-run adapters

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\core\adapters\http_adapter.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\core\adapters\mqtt_adapter.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\core\adapters\home_assistant_adapter.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\tests\test_registry.py`

- [ ] **Step 1: Write the failing test**

```python
def test_builtin_adapters_describe_themselves():
    registry = create_builtin_registry()
    descriptions = {item["adapter_type"]: item for item in registry.describe()}
    assert descriptions["http"]["supports_dry_run"] is True
    assert descriptions["mqtt"]["supports_dry_run"] is True
    assert descriptions["home_assistant"]["supports_dry_run"] is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest main/xuanwu-gateway/tests/test_registry.py -k describe -v`
Expected: FAIL because adapters are not implemented

- [ ] **Step 3: Write minimal implementation**

```python
class HttpAdapter(BaseGatewayAdapter):
    adapter_type = "http"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest main/xuanwu-gateway/tests/test_registry.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-gateway/core/adapters/http_adapter.py main/xuanwu-gateway/core/adapters/mqtt_adapter.py main/xuanwu-gateway/core/adapters/home_assistant_adapter.py main/xuanwu-gateway/tests/test_registry.py
git commit -m "feat: add builtin gateway adapters"
```

### Task 4: 落地命令分发接口

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\core\api\gateway_handler.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\core\http_server.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\tests\test_dispatch.py`

- [ ] **Step 1: Write the failing test**

```python
def test_dispatch_routes_command_to_matching_adapter():
    response = client.post("/gateway/v1/commands:dispatch", json={
        "request_id": "req-001",
        "gateway_id": "gateway-http-001",
        "adapter_type": "http",
        "device_id": "device-001",
        "capability_code": "switch.on_off",
        "command_name": "turn_on",
        "arguments": {"state": True},
    })
    assert response.status_code == 200
    assert response.json()["adapter_type"] == "http"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest main/xuanwu-gateway/tests/test_dispatch.py -v`
Expected: FAIL because handler does not exist

- [ ] **Step 3: Write minimal implementation**

```python
payload = registry.get(body["adapter_type"]).dispatch(body)
return web.json_response(payload)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest main/xuanwu-gateway/tests/test_dispatch.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-gateway/core/api/gateway_handler.py main/xuanwu-gateway/core/http_server.py main/xuanwu-gateway/tests/test_dispatch.py
git commit -m "feat: add gateway dispatch endpoint"
```

### Task 5: 阶段验证与状态同步

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\docs\project\state\current.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\docs\project\tasks\2026-03-30-platform-implementation-roadmap.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-management-server-phase1\main\xuanwu-gateway\README.md`

- [ ] **Step 1: Run target tests**

Run: `python -m pytest main/xuanwu-gateway/tests/test_bootstrap.py main/xuanwu-gateway/tests/test_registry.py main/xuanwu-gateway/tests/test_dispatch.py -q`
Expected: PASS

- [ ] **Step 2: Run broader verification**

Run: `python -m pytest main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py main/xuanwu-management-server/tests/test_xuanwu_proxy_contract.py main/xuanwu-gateway/tests/test_bootstrap.py main/xuanwu-gateway/tests/test_registry.py main/xuanwu-gateway/tests/test_dispatch.py -q`
Expected: PASS

- [ ] **Step 3: Run syntax validation**

Run: `python -m py_compile main/xuanwu-gateway/app.py main/xuanwu-gateway/core/http_server.py main/xuanwu-gateway/core/api/gateway_handler.py main/xuanwu-gateway/core/registry/adapter_registry.py main/xuanwu-gateway/core/contracts/models.py main/xuanwu-gateway/core/adapters/base.py main/xuanwu-gateway/core/adapters/http_adapter.py main/xuanwu-gateway/core/adapters/mqtt_adapter.py main/xuanwu-gateway/core/adapters/home_assistant_adapter.py`
Expected: PASS

- [ ] **Step 4: Update state and roadmap**

```markdown
## Completed
- `xuanwu-gateway` Phase 3 foundation completed

## Next Step
- `xuanwu-device-server` boundary alignment
```

- [ ] **Step 5: Commit**

```bash
git add docs/project/state/current.md docs/project/tasks/2026-03-30-platform-implementation-roadmap.md main/xuanwu-gateway/README.md
git commit -m "docs: record gateway foundation completion"
```
