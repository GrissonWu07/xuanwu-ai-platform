# xuanwu-portal Frontend Spec

Date: 2026-03-31

## Purpose

This spec defines the first real implementation scope for `main/xuanwu-portal`.

It turns the approved visual design into a frontend product specification and clarifies:

- what the portal includes
- which backend APIs it depends on
- which pages are in the first delivery
- which areas are blocked by upstream `XuanWu`

This document is implementation-facing.  
The visual direction remains defined in:

- `C:\Projects\githubs\myaiagent\ai-assist-device\docs\superpowers\specs\2026-03-31-xuanwu-portal-design.md`

## Product Position

`xuanwu-portal` is the single frontend entry for the platform.

It replaces multiple admin entry points with one Vue 3 application that unifies:

- management surfaces
- gateway visibility
- device runtime visibility
- `XuanWu` configuration proxy surfaces

The portal should feel like one product, not several backends stitched together.

## Confirmed Navigation Model

### Primary Navigation

The only primary tabs visible in the main shell are:

- `Overview`
- `Devices`
- `Agents`
- `Jobs`
- `Alerts`

`Overview` is the default landing page.

### Secondary Navigation

Secondary destinations live in the profile dropdown on the top-right.

The dropdown should host:

- `Users & Roles`
- `Channels & Gateways`
- `AI Config Proxy`
- `Telemetry & Alarms`
- `Settings`
- `Sign out`

There is no left sidebar.

## Visual Rules

The portal must preserve these approved visual rules:

- no left navigation rail
- no heavy dark enterprise shell
- light canvas with soft aurora accents
- centered primary tabs
- profile-driven secondary navigation
- rounded cards, soft shadows, restrained emphasis

Approved concept references:

- `C:\Projects\githubs\myaiagent\ai-assist-device\docs\project\designs\2026-03-31-xuanwu-portal-home-concept-v5.png`
- `C:\Projects\githubs\myaiagent\ai-assist-device\docs\project\designs\2026-03-31-xuanwu-portal-devices-concept-v1.png`
- `C:\Projects\githubs\myaiagent\ai-assist-device\docs\project\designs\2026-03-31-xuanwu-portal-agents-concept-v1.png`
- `C:\Projects\githubs\myaiagent\ai-assist-device\docs\project\designs\2026-03-31-xuanwu-portal-jobs-concept-v1.png`
- `C:\Projects\githubs\myaiagent\ai-assist-device\docs\project\designs\2026-03-31-xuanwu-portal-alerts-concept-v1.png`

## Technical Direction

`xuanwu-portal` should be implemented as a new Vue 3 application at:

- `main/xuanwu-portal`

Recommended stack:

- Vue 3
- TypeScript
- Vue Router
- Pinia
- Vite
- a small local component system for shell, cards, tabs, pills, tables, activity feeds, and forms

The portal should not inherit the old `manager-web` build or shell.

## Page Scope

### Phase 1

These pages should be implemented first:

1. Shell
2. `Overview`
3. `Devices`
4. `Jobs`
5. `Alerts`
6. `Agents` shell with live proxy integration when available

### Phase 2

These profile-menu pages can follow:

- `Users & Roles`
- `Channels & Gateways`
- `AI Config Proxy` deeper forms
- `Settings`

## Page Definitions

### Overview

Purpose:

- product home
- summary state
- cross-domain quick actions
- recent operational activity

Required modules:

- top bar
- status pills
- hero summary
- quick cards for `Devices`, `Agents`, `Jobs`, `Alerts`
- `Today Summary`
- `Live Activity`

Primary backend dependency:

- `xuanwu-management-server`

### Devices

Purpose:

- manage and inspect platform devices
- claim and bind devices
- review lifecycle and ownership

Expected content:

- search/filter toolbar
- list/table
- device summary
- selected-device binding and runtime views

Primary backend dependency:

- `xuanwu-management-server`

### Agents

Purpose:

- manage proxy views for Agent-domain resources
- display the `XuanWu` source-of-truth through management APIs

Expected content:

- agents list
- provider/model overview
- proxy health/sync state

Primary backend dependency:

- `xuanwu-management-server` proxy endpoints
- upstream `XuanWu`

This page should degrade gracefully if upstream `XuanWu` is unavailable.

### Jobs

Purpose:

- view schedules
- inspect job runs
- understand scheduler health

Expected content:

- schedules table
- run history
- scheduler status summary

Primary backend dependency:

- `xuanwu-management-server`
- `xuanwu-jobs` health/config endpoints for read-only status

### Alerts

Purpose:

- monitor alarms and operational issues
- acknowledge and inspect active alert state

Expected content:

- alert summary
- alert list
- severity and state chips
- operational anomaly trend

Primary backend dependency:

- `xuanwu-management-server`

## API Consumption Model

The frontend should consume backend APIs by service domain.

### Domain grouping

- `management` domain:
  - users
  - channels
  - devices
  - mappings
  - capabilities
  - ota
  - events
  - telemetry
  - alarms
  - jobs
- `gateway` domain:
  - adapter and gateway operational status
- `device` domain:
  - runtime and device-server operational visibility
- `xuanwu-proxy` domain:
  - agents
  - model providers
  - models

The portal should not treat all APIs as one flat namespace in code.

## Required Frontend Modules

The first implementation should define these reusable modules:

- `shell`
- `topbar`
- `profile-menu`
- `primary-tabs`
- `status-pill`
- `summary-card`
- `activity-feed`
- `data-table`
- `filter-toolbar`
- `empty-state`
- `upstream-unavailable-state`

## Required UX Rules

- Tabs switch workstream context, not arbitrary sub-pages
- Profile menu holds low-frequency administrative navigation
- The shell should remain usable at laptop widths
- Dense information is allowed, but the first screen must stay visually calm
- Agent-domain screens must show clear upstream dependency state

## API Dependency Matrix

### Ready now

Safe to build now:

- `Overview`
- `Devices`
- `Jobs`
- `Alerts`

### Partially ready

Buildable with graceful fallback:

- `Agents`

Reason:

- local proxy routes exist
- live data still depends on upstream `XuanWu`

## Out of Scope for Phase 1

- full RBAC UX
- complete settings UX
- every legacy management page
- deep gateway configuration editing
- final upstream `XuanWu` authored forms beyond proxy scope

## Acceptance Criteria

Phase 1 is complete when:

- `main/xuanwu-portal` exists as a Vue 3 app
- the shell matches the approved design direction
- the shell uses top tabs and profile dropdown, not a left sidebar
- `Overview`, `Devices`, `Jobs`, and `Alerts` are functional against local APIs
- `Agents` is wired to the proxy domain and handles upstream-unavailable state cleanly
- the old `manager-web` shell is no longer the intended primary frontend direction
