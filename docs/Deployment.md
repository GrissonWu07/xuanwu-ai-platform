# 部署指南

本文档描述当前仓库里“本地平台层”的完整 Docker 部署方式。

这条部署路径会启动：

- `xuanwu-portal`
- `xuanwu-management-server`
- `xuanwu-jobs`
- `xuanwu-device-gateway`
- `xuanwu-iot-gateway`
- `mosquitto`
- `postgres`

如果你只想验证当前最小闭环，也可以使用：

```bash
docker compose -f docker-compose.minimal.yml up -d
```

这条最小验证栈只拉起：

- `postgres`
- `xuanwu-management-server`
- `xuanwu-device-gateway`

注意：

- 这套 Compose 启动的是本仓库内的本地平台层，不包含 `XuanWu` 本体。
- 如果你希望 `Agents`、`AI Config Proxy`、上游智能体管理与执行能力真正可用，还需要一个可访问的 `XuanWu` 服务，并正确设置 `XUANWU_BASE_URL`。

## 适用场景

## 默认持久化

当前平台默认使用 PostgreSQL 作为主持久化层：

- `xuanwu-management-server` 使用 schema `xw_mgmt`
- `xuanwu-iot-gateway` 使用 schema `xw_iot`
- PostgreSQL 宿主机数据目录为 `deploy/data/pg`

推荐在这些场景使用全模块部署：

- 需要统一门户 `xuanwu-portal`
- 需要设备纳管、发现设备、告警、任务调度等管理能力
- 需要同时运行会话型设备接入和 IoT 设备接入
- 需要验证本地平台层的完整数据闭环

## 部署前准备

你需要准备：

- 一台已安装 Docker 和 Docker Compose Plugin 的 Linux 主机，或支持 Docker 的开发机
- 本仓库源码
- `SenseVoiceSmall` 的 `model.pt`
- 一个可选但推荐的 `deploy/data/device-gateway/.config.yaml`
- 一个可访问的 `XuanWu` 上游地址
- 根目录 `.env`

## 第一步：获取源码

```bash
git clone https://github.com/GrissonWu07/xuanwu-ai-platform.git
cd xuanwu-ai-platform
```

## 第二步：理解根目录部署锚点

当前部署入口已经提升到仓库根目录。

也就是说，真正的部署锚点现在是：

```text
docker-compose.yml
deploy/
```

其中：

- 根目录 `docker-compose.yml` 是唯一推荐的部署入口
- `deploy/data/device-gateway` 存放 `xuanwu-device-gateway` 的本地覆盖配置和运行时落盘数据
- `deploy/models/SenseVoiceSmall/model.pt` 存放本地模型文件

这层包装不会改变服务内部代码结构，只是把“用户如何部署”统一到了仓库根目录。

## 第三步：准备目录和模型

确保以下目录存在：

```text
deploy/
├─ data
│  └─ device-gateway
└─ models
   └─ SenseVoiceSmall
      └─ model.pt
```

创建目录：

```bash
mkdir -p deploy/data/device-gateway
mkdir -p deploy/data/pg
mkdir -p deploy/logs/postgres
mkdir -p deploy/logs/mosquitto
mkdir -p deploy/logs/portal
mkdir -p deploy/logs/device-gateway
mkdir -p deploy/logs/management-server
mkdir -p deploy/logs/iot-gateway
mkdir -p deploy/logs/jobs
mkdir -p deploy/models/SenseVoiceSmall
```

下载模型文件并放到：

```text
deploy/models/SenseVoiceSmall/model.pt
```

当前仓库里已经包含 `SenseVoiceSmall` 的辅助配置文件：

- `main/xuanwu-device-gateway/models/SenseVoiceSmall/config.yaml`
- `main/xuanwu-device-gateway/models/SenseVoiceSmall/configuration.json`

所以部署时只需要补齐 `model.pt`。

推荐优先使用 ModelScope：

```bash
python -m pip install -U modelscope
python -m modelscope.cli download --model iic/SenseVoiceSmall --file model.pt --local_dir deploy/models/SenseVoiceSmall
```

官方页面：

- [ModelScope - iic/SenseVoiceSmall](https://modelscope.cn/models/iic/SenseVoiceSmall)

如果你的环境访问 Hugging Face 更稳定，也可以直接执行：

```bash
curl -L "https://huggingface.co/FunAudioLLM/SenseVoiceSmall/resolve/main/model.pt" -o deploy/models/SenseVoiceSmall/model.pt
```

官方页面：

- [Hugging Face - FunAudioLLM/SenseVoiceSmall](https://huggingface.co/FunAudioLLM/SenseVoiceSmall)

## 第四步：准备根目录环境配置

根目录部署推荐通过：

```text
.env
```

管理上游地址和关键密钥。

第一次部署前，先复制：

```bash
cp .env.example .env
```

至少确认下面这些值：

```text
XUANWU_BASE_URL=http://你的-xuanwu-地址
XUANWU_CONTROL_PLANE_SECRET=你的-control-plane-secret
```

## 第五步：准备本地覆盖配置

如果你需要做本地覆盖，请创建：

```text
deploy/data/device-gateway/.config.yaml
```

当前 `xuanwu-device-gateway` 的配置加载顺序是：

1. 服务内默认 `config.yaml`
2. 容器内 `/opt/xuanwu-device-gateway/data/.config.yaml`
3. 环境变量覆盖

在根目录部署模式下，`deploy/data/device-gateway/.config.yaml` 会通过 Docker 挂载映射到：

```text
/opt/xuanwu-device-gateway/data/.config.yaml
```

`xuanwu-device-gateway` 运行期间产生的本地短期记忆也会写回宿主机：

```text
deploy/data/device-gateway/.memory.yaml
```

所以你不需要再复制：

- `main/xuanwu-device-gateway/config.yaml`

也不需要再进入服务目录操作。

如果你只想先把整套平台拉起来做联通验证，`deploy/data/device-gateway/.config.yaml` 可以先留空文件。

如果暂时没有 `XuanWu`，本地平台层大部分服务仍然可以启动，但以下能力会受影响：

- `Agents` 页面真实数据
- `AI Config Proxy`
- 智能体执行与设备调用闭环

## 第六步：启动全模块

```bash
docker compose up -d
```

如果只做最小验证：

```bash
docker compose -f docker-compose.minimal.yml up -d
```

查看容器状态：

```bash
docker compose ps
```

查看关键日志：

```bash
docker logs -f xuanwu-management-server
docker logs -f xuanwu-device-gateway
docker logs -f xuanwu-iot-gateway
docker logs -f xuanwu-jobs
docker logs -f xuanwu-portal
```

除了 `docker logs`，宿主机也会保留每个服务的文件日志：

- `deploy/logs/postgres/postgresql.log`
- `deploy/logs/mosquitto/mosquitto.log`
- `deploy/logs/portal/access.log`
- `deploy/logs/portal/error.log`
- `deploy/logs/device-gateway/server.log`
- `deploy/logs/management-server/management-server.log`
- `deploy/logs/iot-gateway/iot-gateway.log`
- `deploy/logs/jobs/jobs.log`

## 端口开放建议

默认全模块部署中，如果你需要对外开放端口，推荐只开放：

- `18081`：`xuanwu-portal`
- `8000`：`xuanwu-device-gateway` WebSocket
- `8003`：`xuanwu-device-gateway` OTA / runtime HTTP / vision explain
- `1883`：`mosquitto`，仅在需要 MQTT 设备接入时开放

这些端口更适合只在容器网络或内网中使用：

- `18082`：`xuanwu-management-server`
- `18083`：`xuanwu-jobs`
- `18084`：`xuanwu-iot-gateway`

PostgreSQL 只在 Docker 内部网络中使用，不再映射宿主机端口。

## 默认端口

默认会暴露这些入口：

- `xuanwu-portal`: `http://127.0.0.1:18081`
- `xuanwu-management-server`: `http://127.0.0.1:18082`
- `xuanwu-jobs`: `http://127.0.0.1:18083/jobs/v1/health`
- `xuanwu-iot-gateway`: `http://127.0.0.1:18084/gateway/v1/health`
- `xuanwu-device-gateway` WebSocket: `ws://127.0.0.1:8000/xuanwu/v1/`
- `xuanwu-device-gateway` OTA: `http://127.0.0.1:8003/xuanwu/ota/`
- `xuanwu-device-gateway` Vision: `http://127.0.0.1:8003/mcp/vision/explain`
- `mosquitto`: `127.0.0.1:1883`

## 启动后如何验证

推荐按下面顺序检查：

1. 打开 `http://127.0.0.1:18081`
2. 确认 `xuanwu-portal` 静态页面能正常加载
3. 确认 `http://127.0.0.1:18084/gateway/v1/health` 返回网关健康信息
4. 确认 `http://127.0.0.1:18083/jobs/v1/health` 返回调度服务健康信息
5. 用设备或模拟上报验证 `xuanwu-device-gateway` / `xuanwu-iot-gateway` 能回写 management

## 常见问题

### 1. 为什么全模块已经启动，但 Agents 页面没有真实数据

因为当前 Compose 不包含 `XuanWu` 本体。你还需要：

- 单独部署 `XuanWu`
- 把 `.env` 里的 `XUANWU_BASE_URL` 指向它
- 对齐管理密钥和执行密钥

### 2. 为什么 `xuanwu-device-gateway` 启动失败

最常见原因是：

- `deploy/models/SenseVoiceSmall/model.pt` 不存在
- `deploy/data/device-gateway/.config.yaml` 里有错误配置
- 挂载目录权限不正确

### 3. 为什么 `xuanwu-portal` 能打开，但部分页面没有数据

常见原因有：

- `xuanwu-management-server` 没起来
- `xuanwu-management-server` 没法访问 `XuanWu`
- 还没有真实设备、发现设备或调度记录

## 停止与重启

停止：

```bash
docker compose down
```

重启：

```bash
docker compose up -d
```

强制重建：

```bash
docker compose up -d --build
```

## 相关阅读

- [快速开始](./quick-start.md)
- [平台交付总览](./platform-delivery-overview.md)
- [设备接入与纳管指南](./device-ingress-and-management-guide.md)

## Docker Hub 自动发布

当前仓库已经提供 GitHub Actions 自动打包并推送到 Docker Hub 的工作流。

首个公开版本标签：

- `v0.7.1`

发布镜像：

- `${DOCKERHUB_USERNAME}/xuanwu-portal`
- `${DOCKERHUB_USERNAME}/xuanwu-device-gateway`
- `${DOCKERHUB_USERNAME}/xuanwu-management-server`
- `${DOCKERHUB_USERNAME}/xuanwu-iot-gateway`
- `${DOCKERHUB_USERNAME}/xuanwu-jobs`

你需要在 GitHub 仓库里配置：

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

工作流触发规则：

- 推送到 `main`：发布 `latest` 与 `sha-<shortsha>`
- 推送语义化标签，例如 `v0.7.1`：发布 `v0.7.1`、`0.7.1` 与 `latest`
- `workflow_dispatch`：手动触发
