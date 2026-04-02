# Docker Hub Release Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add GitHub Actions based Docker Hub publishing for the five active platform services and make `v0.7.1` the first public version tag.

**Architecture:** Add missing service Dockerfiles, replace legacy GHCR workflows with a single Docker Hub matrix release workflow, and document the required secrets and image names. Keep the automation focused on image packaging and publishing only.

**Tech Stack:** GitHub Actions, Docker Buildx, Docker Hub, pytest, Markdown

---

### Task 1: Lock the release automation contract with tests

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\tests\test_dockerhub_release_workflow.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dockerhub_release_workflow_exists() -> None:
    workflow = ROOT / ".github" / "workflows" / "dockerhub-release.yml"
    assert workflow.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_dockerhub_release_workflow.py -q
```

Expected: FAIL because the workflow does not exist yet.

- [ ] **Step 3: Expand the failing test to lock the full contract**

```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dockerhub_release_workflow_contract() -> None:
    workflow = ROOT / ".github" / "workflows" / "dockerhub-release.yml"
    text = workflow.read_text(encoding="utf-8")

    assert "docker/login-action" in text
    assert "DOCKERHUB_USERNAME" in text
    assert "DOCKERHUB_TOKEN" in text
    assert "workflow_dispatch:" in text
    assert "push:" in text
    assert "main" in text
    assert "v*.*.*" in text
    assert "xuanwu-portal" in text
    assert "xuanwu-device-gateway" in text
    assert "xuanwu-management-server" in text
    assert "xuanwu-iot-gateway" in text
    assert "xuanwu-jobs" in text
```

- [ ] **Step 4: Run test to verify it still fails for the right reason**

Run:

```bash
python -m pytest tests/test_dockerhub_release_workflow.py -q
```

Expected: FAIL because the new workflow file and content still do not exist.

- [ ] **Step 5: Commit**

```bash
git add tests/test_dockerhub_release_workflow.py
git commit -m "test: define dockerhub release workflow contract"
```

### Task 2: Add the missing service Dockerfiles

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-device-gateway\Dockerfile`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-management-server\Dockerfile`
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\main\xuanwu-jobs\Dockerfile`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\tests\test_dockerhub_release_workflow.py`

- [ ] **Step 1: Extend the test with Dockerfile existence assertions**

```python
def test_release_dockerfiles_exist() -> None:
    root = ROOT / "main"
    assert (root / "xuanwu-device-gateway" / "Dockerfile").exists()
    assert (root / "xuanwu-management-server" / "Dockerfile").exists()
    assert (root / "xuanwu-jobs" / "Dockerfile").exists()
    assert (root / "xuanwu-iot-gateway" / "Dockerfile").exists()
    assert (root / "xuanwu-portal" / "Dockerfile").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_dockerhub_release_workflow.py -q
```

Expected: FAIL because the three new Dockerfiles do not exist yet.

- [ ] **Step 3: Add the minimal release Dockerfiles**

`main/xuanwu-management-server/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /opt/xuanwu-management-server

COPY main/xuanwu-management-server /opt/xuanwu-management-server

RUN pip install --no-cache-dir aiohttp pyyaml httpx sqlalchemy psycopg[binary]

CMD ["python", "app.py"]
```

`main/xuanwu-jobs/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /opt/xuanwu-jobs

COPY main/xuanwu-jobs /opt/xuanwu-jobs

RUN pip install --no-cache-dir aiohttp pyyaml httpx

CMD ["python", "app.py"]
```

`main/xuanwu-device-gateway/Dockerfile`

```dockerfile
FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libopus0 ffmpeg locales && \
    sed -i '/zh_CN.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV LANG=zh_CN.UTF-8 \
    LC_ALL=zh_CN.UTF-8 \
    LANGUAGE=zh_CN:zh \
    PYTHONIOENCODING=utf-8

WORKDIR /opt/xuanwu-device-gateway

COPY main/xuanwu-device-gateway/requirements.txt /opt/xuanwu-device-gateway/requirements.txt

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY main/xuanwu-device-gateway /opt/xuanwu-device-gateway

CMD ["python", "app.py"]
```

- [ ] **Step 4: Run the Dockerfile contract tests**

Run:

```bash
python -m pytest tests/test_dockerhub_release_workflow.py -q
```

Expected: still FAIL, but now only because the workflow has not been added yet.

- [ ] **Step 5: Commit**

```bash
git add main/xuanwu-device-gateway/Dockerfile main/xuanwu-management-server/Dockerfile main/xuanwu-jobs/Dockerfile tests/test_dockerhub_release_workflow.py
git commit -m "build: add release dockerfiles for active services"
```

### Task 3: Replace legacy GHCR workflows with a Docker Hub release workflow

**Files:**
- Create: `C:\Projects\githubs\myaiagent\ai-assist-device\.github\workflows\dockerhub-release.yml`
- Delete: `C:\Projects\githubs\myaiagent\ai-assist-device\.github\workflows\docker-image.yml`
- Delete: `C:\Projects\githubs\myaiagent\ai-assist-device\.github\workflows\build-base-image.yml`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\tests\test_dockerhub_release_workflow.py`

- [ ] **Step 1: Keep the workflow contract test failing**

Run:

```bash
python -m pytest tests/test_dockerhub_release_workflow.py -q
```

Expected: FAIL because the Docker Hub workflow is still missing.

- [ ] **Step 2: Add the release workflow**

Create `.github/workflows/dockerhub-release.yml` with:

```yaml
name: Docker Hub Release

on:
  push:
    branches:
      - main
    tags:
      - "v*.*.*"
  workflow_dispatch:

jobs:
  publish:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - image: xuanwu-portal
            dockerfile: main/xuanwu-portal/Dockerfile
          - image: xuanwu-device-gateway
            dockerfile: main/xuanwu-device-gateway/Dockerfile
          - image: xuanwu-management-server
            dockerfile: main/xuanwu-management-server/Dockerfile
          - image: xuanwu-iot-gateway
            dockerfile: main/xuanwu-iot-gateway/Dockerfile
          - image: xuanwu-jobs
            dockerfile: main/xuanwu-jobs/Dockerfile

    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - uses: docker/metadata-action@v5
        id: meta
        with:
          images: ${{ secrets.DOCKERHUB_USERNAME }}/${{ matrix.image }}
          tags: |
            type=raw,value=latest,enable={{is_default_branch}}
            type=sha,format=short,prefix=sha-
            type=match,pattern=v(.*),group=0
            type=match,pattern=v(.*),group=1
      - uses: docker/build-push-action@v6
        with:
          context: .
          file: ${{ matrix.dockerfile }}
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

- [ ] **Step 3: Remove the legacy GHCR workflows**

Delete:

- `.github/workflows/docker-image.yml`
- `.github/workflows/build-base-image.yml`

- [ ] **Step 4: Run the workflow tests**

Run:

```bash
python -m pytest tests/test_dockerhub_release_workflow.py -q
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/dockerhub-release.yml .github/workflows/docker-image.yml .github/workflows/build-base-image.yml tests/test_dockerhub_release_workflow.py
git commit -m "ci: publish active service images to docker hub"
```

### Task 4: Document the Docker Hub release process

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\README.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\README_zh.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\docs\Deployment.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\tests\test_xuanwu_management_server_docs.py`

- [ ] **Step 1: Extend the docs test**

Add an assertion like:

```python
def test_docs_describe_dockerhub_release() -> None:
    text = (ROOT / "docs" / "Deployment.md").read_text(encoding="utf-8")
    assert "DOCKERHUB_USERNAME" in text
    assert "DOCKERHUB_TOKEN" in text
    assert "v0.7.1" in text
    assert "xuanwu-portal" in text
    assert "xuanwu-device-gateway" in text
```

- [ ] **Step 2: Run the docs test to verify it fails**

Run:

```bash
python -m pytest tests/test_xuanwu_management_server_docs.py -q
```

Expected: FAIL because the release documentation is missing.

- [ ] **Step 3: Update the documentation**

Document:

- the required GitHub secrets
- the five Docker Hub image names
- that `v0.7.1` is the first version tag
- that pushes to `main` publish `latest`
- that version tags publish versioned tags

- [ ] **Step 4: Run the docs tests**

Run:

```bash
python -m pytest tests/test_xuanwu_management_server_docs.py -q
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md README_zh.md docs/Deployment.md tests/test_xuanwu_management_server_docs.py
git commit -m "docs: describe docker hub image publishing"
```

### Task 5: Run focused regression checks

**Files:**
- No new files

- [ ] **Step 1: Run release workflow tests**

Run:

```bash
python -m pytest tests/test_dockerhub_release_workflow.py tests/test_docs_rename.py tests/test_xuanwu_management_server_docs.py -q
```

Expected: PASS

- [ ] **Step 2: Run Docker-related regression tests**

Run:

```bash
python -m pytest tests/test_root_deploy_entry.py tests/test_xuanwu_portal_docker.py tests/test_xuanwu_iot_gateway_docker.py tests/test_xuanwu_jobs_docker.py -q
```

Expected: PASS

- [ ] **Step 3: Run a syntax sanity check**

Run:

```bash
@'
from pathlib import Path
import yaml

workflow = Path('.github/workflows/dockerhub-release.yml')
yaml.safe_load(workflow.read_text(encoding='utf-8'))
print('workflow yaml ok')
'@ | python -
```

Expected: `workflow yaml ok`

- [ ] **Step 4: Commit final release automation polish if needed**

```bash
git add .
git commit -m "test: finalize docker hub release automation"
```
