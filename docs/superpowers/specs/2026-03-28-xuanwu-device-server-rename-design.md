# Xuanwu Device Server Rename Design

**Date:** 2026-03-28

## Goal

Rename the Python runtime service from `xuanwu-device-server` to `xuanwu-device-server`, and rename the Chinese-facing brand from `灏忔櫤` to `鐜勬AI` across the runtime service, deployment surface, and shared top-level documentation.

## Scope

### In Scope

- Rename `main/xuanwu-device-server` to `main/xuanwu-device-server`
- Update root-level build and deployment references
- Update root README and `docs/` references that point to the runtime service
- Update `main/README.md` and `main/README_en.md`
- Update comments and user-facing Chinese text inside the Python runtime service
- Remove `main/manager-mobile`

### Out of Scope

- `main/manager-api`
- `main/manager-web`
- Java package names such as `xiaozhi.*`
- Protocol paths such as `/xiaozhi`
- Historical external repository URLs, release badges, and star-history targets

## Rename Rules

### Filesystem and Path Names

- `main/xuanwu-device-server` becomes `main/xuanwu-device-server`
- Path references outside `manager-api` and `manager-web` must be updated accordingly

### External Naming

- `xuanwu-device-server` should be renamed to `xuanwu-device-server` in:
  - deployment docs
  - Dockerfiles
  - scripts
  - CI references
  - user-facing instructions

### Chinese Branding

- Chinese-facing `灏忔櫤` becomes `鐜勬AI`
- This applies to:
  - docs
  - comments
  - default visible strings
  - runtime-facing Chinese examples

### Compatibility Exceptions

The following must remain unchanged for now:

- `/xiaozhi` protocol route strings
- Java package namespaces
- existing external repository links
- upstream star/release badge URLs

## Architecture Intent

This is a naming and identity consolidation task, not a protocol migration task. The runtime service remains the same Python system, but its filesystem location, deployment name, and visible branding should now align with `Xuanwu`.

## Risks

- Docker and CI paths may break after the directory rename
- Shell scripts may still assume `/opt/xuanwu-device-server`
- Documentation can drift if root docs and runtime docs are not updated together
- Accidentally renaming `/xiaozhi` protocol paths or Java package names would break compatibility

## Mitigations

- Rename in phases: path surface first, then runtime text, then docs, then cleanup
- Use targeted search for `xuanwu-device-server`, `device_server`, and `灏忔櫤`
- Preserve explicit exception patterns
- Verify with focused tests and path-level checks after each phase

## Testing Strategy

- Add focused tests or assertions for renamed runtime paths where practical
- Run `main/xuanwu-device-server/tests/test_local_control_plane.py`
- Run Python syntax verification for touched runtime files
- Validate path references in Docker and workflow files through grep-based verification
- Perform two manual review passes after each implementation round

## Acceptance Criteria

- `main/xuanwu-device-server` exists and replaces `main/xuanwu-device-server`
- Root build and deployment files point at `main/xuanwu-device-server`
- Runtime-facing docs no longer instruct users to use `main/xuanwu-device-server`
- Chinese docs/comments in scope use `鐜勬AI` instead of `灏忔櫤`
- `main/manager-mobile` is removed
- `manager-api` and `manager-web` remain untouched
- No `/xiaozhi` protocol route is renamed


