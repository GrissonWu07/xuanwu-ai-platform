# xuanwu-portal Design

Date: 2026-03-31

## Summary

`xuanwu-portal` is the single frontend entry for the platform. It replaces the old multi-entry admin experience with one Vue 3 application that presents a calmer, more product-led control surface for:

- `xuanwu-management-server`
- `xuanwu-gateway`
- `xuanwu-device-server`
- `XuanWu` configuration proxy surfaces

The portal should feel like an AI operations product, not a traditional left-nav enterprise console.

## Goals

- Create one unified frontend entry at `main/xuanwu-portal`
- Rebuild with Vue 3 instead of inheriting the old `manager-web` app
- Use a modern, Atlas-Aurora-inspired visual language without copying the old layout structure
- Keep the first screen focused on clarity, status, and actionability
- Make primary workstreams accessible through centered top tabs
- Move lower-frequency management functions into the profile dropdown

## Non-Goals

- Recreate the legacy `manager-web` information architecture one-to-one
- Preserve the old left sidebar navigation
- Implement every legacy page in the first delivery
- Put Agent-domain source-of-truth logic into this repo

## Primary Information Architecture

### Global Structure

`xuanwu-portal` uses a top navigation shell instead of a left navigation shell.

The shell contains:

- Brand area on the top-left
- Global search in the top center-left
- Lightweight status pills in the top center-right
- Notifications and user profile on the top-right
- Centered primary tabs below the top bar

### Primary Tabs

These are the only first-level workstreams shown directly in the main layout:

- `Overview`
- `Devices`
- `Agents`
- `Jobs`
- `Alerts`

`Overview` is the default landing screen.

### Profile Dropdown

Most lower-frequency or administrative functions move into the profile dropdown instead of staying visible at all times.

The dropdown should hold entries such as:

- `Users & Roles`
- `Channels & Gateways`
- `AI Config Proxy`
- `Telemetry & Alarms`
- `Settings`
- `Sign out`

This keeps the main interface product-like while preserving access to deeper governance functions.

## Visual Direction

The approved direction is a light command-center UI with soft aurora accents.

### Confirmed Decisions

- No left sidebar
- No dark full-height admin rail
- User profile lives in the top-right
- Main workstreams are centered tabs
- The overview hero uses a light surface with soft aurora glow instead of a high-contrast black panel

### Style Characteristics

- Large rounded containers
- Soft shadows
- Neutral light canvas
- Purple-blue accent color
- Aurora-like glow in highlight areas
- High information density without becoming table-first

### Reference Artifact

Approved concept image:

- `C:\Projects\githubs\myaiagent\ai-assist-device\docs\project\designs\2026-03-31-xuanwu-portal-home-concept-v5.png`

## Overview Dashboard Layout

The `Overview` page is the default home screen.

### Top Bar

- Brand and product identity
- Search field
- Status pills such as device count, active channels, and jobs health
- Notification badge
- Avatar and profile dropdown trigger

### Main Tab Row

The central row switches the portal between:

- `Overview`
- `Devices`
- `Agents`
- `Jobs`
- `Alerts`

The active tab is visually prominent with a filled accent chip.

### Hero Section

The hero should:

- introduce the platform state
- summarize what the unified portal manages
- offer 1 to 2 primary actions

The approved version uses:

- a light card
- soft glow background
- dark text
- strong but restrained CTA buttons

### Supporting Cards

The overview below the hero should expose four immediate domain cards:

- `Devices`
- `Agents`
- `Jobs`
- `Alerts`

These cards summarize the state of each domain and act as quick entry points into the dedicated tabs.

### Right Rail

The right side of the screen should hold:

- `Today Summary`
- `Live Activity`

This keeps operational awareness visible without overwhelming the primary work area.

## Module Mapping

### Overview

Purpose:

- product home
- live status
- quick actions
- cross-domain summary

### Devices

Purpose:

- device ownership
- lifecycle
- claims
- binding state
- runtime views

### Agents

Purpose:

- proxy views for Agent, provider, and model configuration through `XuanWu`

### Jobs

Purpose:

- schedules
- job runs
- dispatch results
- health of `xuanwu-jobs`

### Alerts

Purpose:

- alarms
- escalations
- active issues
- recent operational signals

## Migration Strategy

`xuanwu-portal` should be implemented as a new Vue 3 application.

Migration should happen by module, not by copying the whole old frontend.

Recommended order:

1. Shell and top-level layout
2. `Overview`
3. `Devices`
4. `Jobs`
5. `Alerts`
6. `Agents`
7. Profile dropdown destinations

Legacy `manager-web` should be treated as a source of page inventory and domain knowledge, not as the app shell to preserve.

## Technical Direction

The portal should be built as:

- Vue 3
- modern router and state management suitable for modular growth
- one frontend package at `main/xuanwu-portal`

The shell should support:

- responsive top navigation
- modular page routing
- unified auth/session handling
- API separation by backend domain

## Initial Implementation Scope

The first implementation slice should include:

- top shell
- search and profile shell components
- centered primary tab navigation
- `Overview` page
- first real `Devices` work page
- shared card, pill, button, and activity list primitives

## Risks and Guardrails

### Risks

- Over-reusing `manager-web` patterns could pull the new app back into a legacy admin look
- Over-stylizing the hero could make the home page feel like a marketing page instead of an operational product
- Putting too many items in top navigation would recreate clutter in a new place

### Guardrails

- Keep first-level navigation to exactly five tabs
- Put secondary governance functions in the profile dropdown
- Use visual emphasis sparingly
- Prefer activity, status, and action over decorative panels

## Acceptance Criteria

The design is considered correct if:

- there is no left sidebar
- the profile menu is the secondary navigation host
- the primary navigation is `Overview / Devices / Agents / Jobs / Alerts`
- the hero remains light and low-contrast relative to the page
- the portal reads as one unified product instead of multiple backend tools stitched together
