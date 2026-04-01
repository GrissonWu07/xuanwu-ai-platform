# PostgreSQL Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace YAML-backed management persistence with PostgreSQL + SQLAlchemy, add PostgreSQL-backed IoT gateway device state, and make root Docker deployment start PostgreSQL by default.

**Architecture:** `xuanwu-management-server` becomes the durable source of truth through a SQLAlchemy-backed store in schema `xw_mgmt`, while `xuanwu-iot-gateway` stores its device shadow in schema `xw_iot`. Root deployment gains a default PostgreSQL service and the old YAML control plane is preserved only as an import source.

**Tech Stack:** PostgreSQL, SQLAlchemy ORM, aiohttp, pytest, Docker Compose

---

### Task 1: Add PostgreSQL deployment foundation

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\docker-compose.yml`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.env.example`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\docker-setup.sh`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.gitignore`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\deploy\postgres\.gitkeep`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\tests\test_root_deploy_entry.py`

- [ ] **Step 1: Write the failing deployment assertions**

Update `C:\Projects\githubs\myaiagent\ai-assist-device\tests\test_root_deploy_entry.py` to assert:

```python
def test_root_compose_includes_postgres_service() -> None:
    content = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "postgres:" in content
    assert "./deploy/postgres:/var/lib/postgresql/data" in content
    assert "XUANWU_PG_DB=" in content
    assert "XUANWU_MGMT_PG_SCHEMA=" in content
    assert "XUANWU_IOT_PG_SCHEMA=" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_root_deploy_entry.py -q
```

Expected: FAIL because the root compose file does not yet contain PostgreSQL.

- [ ] **Step 3: Add PostgreSQL service and env wiring**

Update `C:\Projects\githubs\myaiagent\ai-assist-device\docker-compose.yml` to add:

- a `postgres` service
- host volume `./deploy/postgres:/var/lib/postgresql/data`
- database env vars for `xuanwu-management-server`
- database env vars for `xuanwu-iot-gateway`

Update `C:\Projects\githubs\myaiagent\ai-assist-device\.env.example` to add:

```env
XUANWU_PG_HOST=postgres
XUANWU_PG_PORT=5432
XUANWU_PG_DB=xuanwu_platform
XUANWU_PG_USER=xuanwu
XUANWU_PG_PASSWORD=xuanwu_local_password
XUANWU_MGMT_PG_SCHEMA=xw_mgmt
XUANWU_IOT_PG_SCHEMA=xw_iot
```

Update `C:\Projects\githubs\myaiagent\ai-assist-device\docker-setup.sh` so it creates:

```sh
POSTGRES_DATA_DIR="$PROJECT_ROOT/deploy/postgres"
mkdir -p "$POSTGRES_DATA_DIR"
```

Update `C:\Projects\githubs\myaiagent\ai-assist-device\.gitignore` to ignore `deploy/postgres/` while allowing `deploy/postgres/.gitkeep`.

- [ ] **Step 4: Run deployment tests**

Run:

```bash
python -m pytest tests/test_root_deploy_entry.py -q
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml .env.example docker-setup.sh .gitignore deploy/postgres/.gitkeep tests/test_root_deploy_entry.py
git commit -m "chore: add postgres root deployment"
```

### Task 2: Introduce management database infrastructure

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\db\engine.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\db\session.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\db\bootstrap.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\db\models.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\store\base.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\app.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_pg_runtime_config.py`

- [ ] **Step 1: Write the failing runtime config test**

Create `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_pg_runtime_config.py`:

```python
from app import load_runtime_config


def test_load_runtime_config_reads_postgres_env(monkeypatch):
    monkeypatch.setenv("XUANWU_PG_HOST", "postgres")
    monkeypatch.setenv("XUANWU_PG_PORT", "5432")
    monkeypatch.setenv("XUANWU_PG_DB", "xuanwu_platform")
    monkeypatch.setenv("XUANWU_PG_USER", "xuanwu")
    monkeypatch.setenv("XUANWU_PG_PASSWORD", "secret")
    monkeypatch.setenv("XUANWU_MGMT_PG_SCHEMA", "xw_mgmt")

    config = load_runtime_config()

    assert config["control-plane"]["backend"] == "postgres"
    assert config["control-plane"]["postgres"]["host"] == "postgres"
    assert config["control-plane"]["postgres"]["schema"] == "xw_mgmt"
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python -m pytest main/xuanwu-management-server/tests/test_pg_runtime_config.py -q
```

Expected: FAIL because runtime config does not yet expose PostgreSQL settings.

- [ ] **Step 3: Add SQLAlchemy bootstrap files and config loading**

Implement:

- `engine.py` to build a SQLAlchemy engine from config
- `session.py` to expose session factories
- `bootstrap.py` to create schema and tables
- `models.py` to define declarative base and initial management tables
- `base.py` to define the control-plane store interface

Update `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\app.py` so `load_runtime_config()` returns:

```python
"control-plane": {
    "secret": auth_key,
    "backend": os.environ.get("XUANWU_CONTROL_PLANE_BACKEND", "postgres"),
    "postgres": {
        "host": os.environ.get("XUANWU_PG_HOST", "postgres").strip(),
        "port": int(os.environ.get("XUANWU_PG_PORT", "5432")),
        "database": os.environ.get("XUANWU_PG_DB", "xuanwu_platform").strip(),
        "user": os.environ.get("XUANWU_PG_USER", "xuanwu").strip(),
        "password": os.environ.get("XUANWU_PG_PASSWORD", "xuanwu_local_password").strip(),
        "schema": os.environ.get("XUANWU_MGMT_PG_SCHEMA", "xw_mgmt").strip(),
    },
},
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
python -m pytest main/xuanwu-management-server/tests/test_pg_runtime_config.py -q
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-management-server/app.py main/xuanwu-management-server/core/db main/xuanwu-management-server/core/store/base.py main/xuanwu-management-server/tests/test_pg_runtime_config.py
git commit -m "feat: add management postgres runtime config"
```

### Task 3: Implement PostgreSQL-backed management store

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\store\local_store.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\store\sqlalchemy_store.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\api\control_plane_handler.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\core\http_server.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_pg_store_contract.py`

- [ ] **Step 1: Write the failing store contract test**

Create `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_pg_store_contract.py` with a minimal temporary PostgreSQL-backed contract:

```python
def test_pg_store_round_trips_user_device_and_schedule(pg_store):
    pg_store.create_user({"user_id": "u1", "name": "User 1"})
    pg_store.save_device("d1", {"device_id": "d1", "user_id": "u1"})
    pg_store.create_schedule({"schedule_id": "s1", "job_type": "device_command"})

    assert pg_store.get_user("u1")["user_id"] == "u1"
    assert pg_store.get_device("d1")["device_id"] == "d1"
    assert pg_store.get_schedule("s1")["schedule_id"] == "s1"
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python -m pytest main/xuanwu-management-server/tests/test_pg_store_contract.py -q
```

Expected: FAIL because `SQLAlchemyControlPlaneStore` does not yet exist.

- [ ] **Step 3: Implement `SQLAlchemyControlPlaneStore`**

In `sqlalchemy_store.py`:

- implement the public methods currently used by handlers
- use SQLAlchemy ORM models and JSON columns
- preserve existing return shapes

In `http_server.py` and `control_plane_handler.py`:

- instantiate the PostgreSQL-backed store by default
- keep handler method signatures unchanged

Leave `local_store.py` in place for import tooling and as a contract reference.

- [ ] **Step 4: Run core management tests**

Run:

```bash
python -m pytest main/xuanwu-management-server/tests/test_pg_store_contract.py main/xuanwu-management-server/tests/test_local_control_plane.py main/xuanwu-management-server/tests/test_http_routes.py -q
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-management-server/core/store/sqlalchemy_store.py main/xuanwu-management-server/core/http_server.py main/xuanwu-management-server/core/api/control_plane_handler.py main/xuanwu-management-server/tests/test_pg_store_contract.py
git commit -m "feat: switch management control plane to postgres store"
```

### Task 4: Add YAML-to-PostgreSQL import path

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\scripts\import_yaml_control_plane.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\tests\test_yaml_import.py`

- [ ] **Step 1: Write the failing import test**

Create `test_yaml_import.py`:

```python
def test_import_yaml_control_plane_imports_devices_and_users(tmp_path, pg_store):
    # prepare a tiny YAML tree in tmp_path
    # run import function
    # assert imported rows exist in postgres
```

Use explicit fixture data:

- `users/u1.yaml`
- `devices/d1.yaml`

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python -m pytest main/xuanwu-management-server/tests/test_yaml_import.py -q
```

Expected: FAIL because the import script does not yet exist.

- [ ] **Step 3: Implement import script**

`import_yaml_control_plane.py` should:

- instantiate `LocalControlPlaneStore` against a source directory
- instantiate `SQLAlchemyControlPlaneStore` against PostgreSQL
- upsert all supported entities
- preserve ids and timestamps

- [ ] **Step 4: Run import tests**

Run:

```bash
python -m pytest main/xuanwu-management-server/tests/test_yaml_import.py -q
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-management-server/scripts/import_yaml_control_plane.py main/xuanwu-management-server/tests/test_yaml_import.py
git commit -m "feat: add yaml to postgres import for control plane"
```

### Task 5: Add PostgreSQL-backed IoT gateway device state

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-iot-gateway\core\db\engine.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-iot-gateway\core\db\session.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-iot-gateway\core\db\bootstrap.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-iot-gateway\core\db\models.py`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-iot-gateway\core\state\sqlalchemy_state_store.py`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-iot-gateway\core\api\gateway_handler.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-iot-gateway\tests\test_pg_device_state.py`

- [ ] **Step 1: Write the failing gateway state test**

Create `test_pg_device_state.py`:

```python
async def test_gateway_state_persists_last_command(pg_gateway_handler):
    result = await pg_gateway_handler.handle_dispatch_command(fake_request(...))
    payload = await read_json(result)
    state = pg_gateway_handler.state_store.get_device_state("device-1")
    assert state["device_id"] == "device-1"
    assert state["last_command_name"] == "turn_on"
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python -m pytest main/xuanwu-iot-gateway/tests/test_pg_device_state.py -q
```

Expected: FAIL because the gateway still uses in-memory state.

- [ ] **Step 3: Implement durable state store**

Add:

- PostgreSQL runtime config loading for the gateway
- SQLAlchemy model for `xw_iot.device_state`
- `sqlalchemy_state_store.py`

Update `gateway_handler.py` so:

- `self.device_state` is removed or demoted to compatibility glue
- command dispatch writes device state via the state store
- ingest paths update last seen state
- bridge event paths update state as well

- [ ] **Step 4: Run gateway tests**

Run:

```bash
python -m pytest main/xuanwu-iot-gateway/tests/test_pg_device_state.py main/xuanwu-iot-gateway/tests -q
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-iot-gateway/core/db main/xuanwu-iot-gateway/core/state/sqlalchemy_state_store.py main/xuanwu-iot-gateway/core/api/gateway_handler.py main/xuanwu-iot-gateway/tests/test_pg_device_state.py
git commit -m "feat: persist iot gateway device state in postgres"
```

### Task 6: Wire management and gateway images to SQLAlchemy dependencies

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-iot-gateway\Dockerfile`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-iot-gateway\requirements.txt`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\docker-compose.yml`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\tests\test_xuanwu_iot_gateway_docker.py`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\tests\test_root_deploy_entry.py`

- [ ] **Step 1: Write the failing dependency assertion**

Add a test that asserts:

- SQLAlchemy driver dependency exists
- PostgreSQL env vars are passed to the gateway and management services

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
python -m pytest tests/test_root_deploy_entry.py tests/test_xuanwu_iot_gateway_docker.py -q
```

Expected: FAIL if dependency wiring is still incomplete.

- [ ] **Step 3: Add dependencies**

Add:

- `sqlalchemy`
- `psycopg[binary]` or `psycopg2-binary`

to the services that need database access.

- [ ] **Step 4: Run deployment tests**

Run:

```bash
python -m pytest tests/test_root_deploy_entry.py tests/test_xuanwu_iot_gateway_docker.py -q
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-iot-gateway/Dockerfile main/xuanwu-iot-gateway/requirements.txt docker-compose.yml tests/test_root_deploy_entry.py tests/test_xuanwu_iot_gateway_docker.py
git commit -m "chore: wire postgres dependencies into gateway deployment"
```

### Task 7: Update docs for PostgreSQL-first persistence

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\docs\quick-start.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\docs\Deployment.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\docs\current-platform-capabilities.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\docs\current-api-surfaces.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\docs\platform-delivery-overview.md`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\tests\test_xuanwu_management_server_docs.py`

- [ ] **Step 1: Write the failing documentation assertion**

Add assertions that docs mention:

- PostgreSQL is the default platform persistence layer
- `xw_mgmt`
- `xw_iot`
- `deploy/postgres`

- [ ] **Step 2: Run docs test to verify failure**

Run:

```bash
python -m pytest tests/test_xuanwu_management_server_docs.py -q
```

Expected: FAIL before the docs are updated.

- [ ] **Step 3: Update docs**

Make documentation state clearly:

- platform truth is in PostgreSQL
- `xuanwu-device-gateway` still uses host-mounted local files
- root deployment starts PostgreSQL by default

- [ ] **Step 4: Run docs tests**

Run:

```bash
python -m pytest tests/test_xuanwu_management_server_docs.py tests/test_root_deploy_entry.py -q
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add docs/quick-start.md docs/Deployment.md docs/current-platform-capabilities.md docs/current-api-surfaces.md docs/platform-delivery-overview.md tests/test_xuanwu_management_server_docs.py
git commit -m "docs: describe postgres-first persistence"
```

### Task 8: Full verification and cleanup

**Files:**
- Verify only

- [ ] **Step 1: Run full targeted regression**

Run:

```bash
python -m pytest main/xuanwu-management-server/tests main/xuanwu-iot-gateway/tests tests/test_root_deploy_entry.py tests/test_xuanwu_iot_gateway_docker.py tests/test_xuanwu_management_server_docs.py -q
```

Expected: PASS

- [ ] **Step 2: Run portal and deployment smoke tests**

Run:

```bash
python -m pytest tests/test_xuanwu_portal_docker.py tests/test_xuanwu_jobs_docker.py -q
```

Expected: PASS

- [ ] **Step 3: Run Python syntax verification**

Run:

```bash
python -m py_compile main/xuanwu-management-server/app.py main/xuanwu-management-server/core/http_server.py main/xuanwu-management-server/core/store/sqlalchemy_store.py main/xuanwu-iot-gateway/core/api/gateway_handler.py main/xuanwu-iot-gateway/core/state/sqlalchemy_state_store.py
```

Expected: no output

- [ ] **Step 4: Commit final integration fixes**

```bash
git add -A
git commit -m "chore: finalize postgres persistence integration"
```

## Self-Review

Spec coverage:

- PostgreSQL deployment foundation: covered by Task 1
- management SQLAlchemy infrastructure: covered by Task 2
- management PG-backed truth: covered by Task 3
- YAML import path: covered by Task 4
- iot gateway durable device state: covered by Task 5
- dependency and image wiring: covered by Task 6
- docs update: covered by Task 7
- verification: covered by Task 8

Placeholder scan:

- No `TODO`, `TBD`, or dangling “add tests later” steps remain.

Type consistency:

- `xw_mgmt` and `xw_iot` schema names are used consistently.
- `SQLAlchemyControlPlaneStore` is the planned management store name throughout.
- `sqlalchemy_state_store.py` is the planned gateway durable state store throughout.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/postgres-persistence-implementation-plan.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
