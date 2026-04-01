# Main Modules

This directory contains the active local platform modules.

## Active Services

- `xuanwu-management-server`
  - control plane
  - management truth
  - portal-facing read models
- `xuanwu-device-gateway`
  - conversational device ingress
  - runtime session handling
  - OTA and runtime execution entrypoints
- `xuanwu-iot-gateway`
  - IoT, industrial, sensor, actuator, and wireless protocol gateway
- `xuanwu-jobs`
  - lightweight scheduler-dispatcher
- `xuanwu-portal`
  - unified frontend entrypoint
- `xuanwu-bluetooth-bridge`
  - standalone Bluetooth bridge service
- `xuanwu-nearlink-bridge`
  - standalone NearLink bridge service

## Current Architecture

The local platform follows this split:

- management truth in `xuanwu-management-server`
- conversational device ingress in `xuanwu-device-gateway`
- IoT and industrial ingress in `xuanwu-iot-gateway`
- scheduling in `xuanwu-jobs`
- user-facing operations in `xuanwu-portal`

## Current Documentation

Start with:

- [Current Platform Capabilities](../docs/current-platform-capabilities.md)
- [Current API Surfaces](../docs/current-api-surfaces.md)
- [Device Ingress and Management Guide](../docs/device-ingress-and-management-guide.md)
- [Spec Completion Status](../docs/superpowers/specs/2026-03-31-spec-completion-status.md)

## Status

Repository-local implementation for the active spec set is complete.

The remaining major blocker is upstream `XuanWu` integration.
