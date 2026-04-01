# Xuanwu Device Server Rename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the Python runtime service to `xuanwu-device-gateway`, update in-scope docs and runtime branding to `鐜勬AI`, and remove `manager-mobile` without touching `manager-api` or `manager-web`.

**Architecture:** This work is a staged rename with strict compatibility exceptions. We first update paths and engineering surface, then update runtime-visible strings and comments, then update shared docs, and finally delete `manager-mobile` and run cross-cutting verification.

**Tech Stack:** Git worktrees, Python, Dockerfiles, GitHub Actions, Markdown docs, shell scripts, pytest

---

### Task 1: Rename Runtime Directory and Engineering Paths

**Files:**
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\.github\dependabot.yml`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\.github\workflows\build-base-image.yml`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\.github\workflows\docker-image.yml`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\.gitignore`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\Dockerfile-server`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\Dockerfile-server-base`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\docker-setup.sh`
- Rename: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\main\xuanwu-device-gateway` -> `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\main\xuanwu-device-gateway`
- Test: grep verification plus runtime test import path checks

- [ ] **Step 1: Add a focused rename regression test**

Create a small pytest file:

```python
from pathlib import Path


def test_runtime_directory_renamed():
    root = Path(__file__).resolve().parents[3]
    assert (root / "main" / "xuanwu-device-gateway").exists()
    assert not (root / "main" / "xuanwu-device-gateway").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_repo_layout.py -q`
Expected: FAIL because `main/xuanwu-device-gateway` does not exist yet

- [ ] **Step 3: Rename the directory and update path references**

Apply the rename and update the engineering files listed above so they point to `main/xuanwu-device-gateway` and the matching `/opt/xuanwu-device-gateway` runtime path where applicable.

- [ ] **Step 4: Run targeted verification**

Run:
- `python -m pytest tests/test_repo_layout.py -q`
- `git grep -n "main/xuanwu-device-gateway"`
- `git grep -n "/opt/xuanwu-device-gateway"`

Expected:
- pytest PASS
- grep only returns allowed legacy exceptions or no matches in in-scope files

- [ ] **Step 5: Review round 1 and fix findings**

Review for:
- broken path references
- Docker/script mismatch
- accidental changes in `manager-api` or `manager-web`

- [ ] **Step 6: Review round 2 and fix findings**

Review for:
- CI path coverage
- `.gitignore` updates for renamed paths
- missed top-level references

### Task 2: Update Runtime Strings, Comments, and Visible Defaults

**Files:**
- Modify: selected files under `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\main\xuanwu-device-gateway`
- Test: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\main\xuanwu-device-gateway\tests\test_local_control_plane.py`

- [ ] **Step 1: Add a focused branding regression test**

Create assertions against representative runtime config and helper files:

```python
from pathlib import Path


def test_runtime_branding_uses_xuanwu_ai():
    root = Path(__file__).resolve().parents[3] / "main" / "xuanwu-device-gateway"
    config_text = (root / "config.yaml").read_text(encoding="utf-8")
    assert "鐜勬AI" in config_text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_repo_branding.py -q`
Expected: FAIL because runtime strings still include `灏忔櫤`

- [ ] **Step 3: Update runtime comments and user-facing Chinese text**

Change in-scope visible strings and comments from `灏忔櫤` to `鐜勬AI`, while preserving `/xuanwu` route strings and other compatibility exceptions.

- [ ] **Step 4: Run targeted runtime verification**

Run:
- `python -m pytest tests/test_repo_branding.py -q`
- `python -m pytest main/xuanwu-device-gateway/tests/test_local_control_plane.py -q`
- `python -m py_compile main/xuanwu-device-gateway/app.py`

Expected:
- branding test PASS
- control-plane test PASS
- py_compile exit 0

- [ ] **Step 5: Review round 1 and fix findings**

Review for:
- protocol strings accidentally changed
- comments changed but code semantics not broken

- [ ] **Step 6: Review round 2 and fix findings**

Review for:
- remaining in-scope `灏忔櫤` strings
- remaining in-scope `xuanwu-device-gateway` comments

### Task 3: Update Root and Shared Documentation

**Files:**
- Modify: root `README*.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\docs\*.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\main\README.md`
- Modify: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\main\README_en.md`

- [ ] **Step 1: Add a documentation regression test**

Create a repository text scan test:

```python
from pathlib import Path


def test_root_docs_use_xuanwu_device_server():
    root = Path(__file__).resolve().parents[3]
    text = (root / "README.md").read_text(encoding="utf-8")
    assert "xuanwu-device-gateway" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_docs_rename.py -q`
Expected: FAIL because root docs still reference `xuanwu-device-gateway`

- [ ] **Step 3: Update in-scope docs**

Rename doc references from `xuanwu-device-gateway` to `xuanwu-device-gateway` and `灏忔櫤` to `鐜勬AI`, while leaving external repository targets unchanged.

- [ ] **Step 4: Run documentation verification**

Run:
- `python -m pytest tests/test_docs_rename.py -q`
- `git grep -n "xuanwu-device-gateway" -- README.md README_en.md README_de.md README_pt_BR.md README_vi.md docs main/README.md main/README_en.md`
- `git grep -n "灏忔櫤" -- README.md docs main/README.md main/xuanwu-device-gateway`

Expected:
- pytest PASS
- grep output only shows approved exceptions or no matches

- [ ] **Step 5: Review round 1 and fix findings**

Review for:
- broken local file links after directory rename
- untouched deployment instructions

- [ ] **Step 6: Review round 2 and fix findings**

Review for:
- phrasing consistency between Chinese and English docs
- accidental references inside excluded `manager-api/web`

### Task 4: Remove manager-mobile

**Files:**
- Delete: `C:\Projects\githubs\myaiagent\ai-assist-device\.worktrees\xuanwu-device-gateway-rename\main\manager-mobile`
- Modify: docs or readmes that mention `manager-mobile`

- [ ] **Step 1: Add a focused deletion regression test**

Create:

```python
from pathlib import Path


def test_manager_mobile_removed():
    root = Path(__file__).resolve().parents[3]
    assert not (root / "main" / "manager-mobile").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_manager_mobile_removed.py -q`
Expected: FAIL because `main/manager-mobile` still exists

- [ ] **Step 3: Remove the directory and clean references**

Delete `main/manager-mobile` and remove or rewrite any in-scope references that claim it is part of the supported architecture.

- [ ] **Step 4: Run targeted verification**

Run:
- `python -m pytest tests/test_manager_mobile_removed.py -q`
- `git grep -n "manager-mobile"`

Expected:
- pytest PASS
- grep only shows historical mentions outside in-scope files or none

- [ ] **Step 5: Review round 1 and fix findings**

Review for:
- accidental partial deletion
- stale docs references

- [ ] **Step 6: Review round 2 and fix findings**

Review for:
- build scripts still assuming mobile app exists

### Task 5: Final Cross-Cutting Verification

**Files:**
- Verify all files touched in Tasks 1-4

- [ ] **Step 1: Run consolidated test suite**

Run:
- `python -m pytest tests/test_repo_layout.py tests/test_repo_branding.py tests/test_docs_rename.py tests/test_manager_mobile_removed.py -q`
- `python -m pytest main/xuanwu-device-gateway/tests/test_local_control_plane.py -q`

Expected: PASS

- [ ] **Step 2: Run cross-cutting grep verification**

Run:
- `git grep -n "main/xuanwu-device-gateway"`
- `git grep -n "/opt/xuanwu-device-gateway"`
- `git grep -n "灏忔櫤" -- README.md docs main/README.md main/xuanwu-device-gateway`

Expected: no in-scope leftovers beyond explicit compatibility exceptions

- [ ] **Step 3: Run syntax verification**

Run:
- `python -m py_compile main/xuanwu-device-gateway/app.py`

Expected: exit 0

- [ ] **Step 4: Review round 1 and fix findings**

Review the final diff for:
- excluded areas accidentally changed
- path or docs inconsistencies

- [ ] **Step 5: Review round 2 and fix findings**

Review the final diff for:
- acceptance criteria coverage
- leftover rename gaps


