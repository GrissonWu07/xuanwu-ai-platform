# xuanwu-jobs

`xuanwu-jobs` is the platform scheduler-dispatcher service.

Current scope:

- poll due schedules from `xuanwu-management-server`
- claim due schedules
- dispatch jobs directly to local execution APIs
- keep `schedule` truth in `xuanwu-management-server`
- stay lightweight and non-authoritative

Current phase does not execute Agent jobs locally in this repository. Agent execution remains an upstream `XuanWu` contract.

## Local dispatch targets

Default Docker wiring includes:

- `xuanwu-jobs`
- `xuanwu-management-server`
- `xuanwu-iot-gateway`
- `xuanwu-device-gateway`

Execution paths:

- platform jobs -> `POST /control-plane/v1/jobs:execute`
- gateway jobs -> `POST /gateway/v1/jobs:execute`
- device jobs -> `POST /runtime/v1/jobs:execute`
