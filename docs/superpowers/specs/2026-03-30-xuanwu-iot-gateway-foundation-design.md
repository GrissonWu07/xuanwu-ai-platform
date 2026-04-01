# xuanwu-iot-gateway Foundation Design

## Goal

落地独立的 `main/xuanwu-iot-gateway` 模块，作为本项目统一的南向协议与设备能力适配层。

## Scope

本阶段只实现基础骨架和首批适配器，不实现真实外部设备联调：

- 独立 Python 服务入口
- 统一命令合同
- adapter registry
- 首批 adapter：
  - `http`
  - `mqtt`
  - `home_assistant`
- 最小 HTTP API：
  - `GET /gateway/v1/adapters`
  - `POST /gateway/v1/commands:dispatch`

## Boundaries

- `xuanwu-management-server`
  - 负责网关目录、能力目录、能力路由和设备治理
- `XuanWu`
  - 负责 Agent 决策，产出标准能力命令
- `xuanwu-iot-gateway`
  - 只负责把标准能力命令路由到具体协议 adapter
  - 返回标准执行结果、事件和遥测
- `xuanwu-device-gateway`
  - 不承载南向协议适配逻辑

## Contract

### Command Request

```json
{
  "request_id": "req-001",
  "gateway_id": "gateway-http-001",
  "adapter_type": "http",
  "device_id": "device-001",
  "capability_code": "switch.on_off",
  "command_name": "turn_on",
  "arguments": {
    "state": true
  }
}
```

### Command Result

```json
{
  "request_id": "req-001",
  "gateway_id": "gateway-http-001",
  "adapter_type": "http",
  "status": "accepted",
  "result": {
    "device_id": "device-001",
    "capability_code": "switch.on_off",
    "command_name": "turn_on"
  },
  "events": [],
  "telemetry": []
}
```

## Adapter Model

每个 adapter 必须实现统一接口：

- `adapter_type`
- `describe()`
- `dispatch(command: dict) -> dict`

首批 adapter 先做标准化 dry-run 执行：

- `http`
  - 保留 `endpoint`、`method`、`headers` 等透传字段
- `mqtt`
  - 保留 `topic`、`qos`、`payload_template` 等透传字段
- `home_assistant`
  - 保留 `entity_id`、`service`、`service_data` 等透传字段

## Directory Layout

```text
main/xuanwu-iot-gateway/
  app.py
  README.md
  core/
    http_server.py
    api/gateway_handler.py
    registry/adapter_registry.py
    contracts/models.py
    adapters/
      base.py
      http_adapter.py
      mqtt_adapter.py
      home_assistant_adapter.py
  tests/
    test_bootstrap.py
    test_registry.py
    test_dispatch.py
```

## Validation

本阶段完成后必须满足：

- `xuanwu-iot-gateway` 可独立启动
- registry 能列出 3 个 adapter
- `commands:dispatch` 能按 `adapter_type` 正确路由
- 每个 adapter 都返回标准结果结构
- 未知 adapter 返回稳定 `404`
