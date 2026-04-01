# 部署指南

本文档描述当前仓库里“本地平台层”的完整 Docker 部署方式。

这条部署路径会启动：

- `xuanwu-portal`
- `xuanwu-management-server`
- `xuanwu-jobs`
- `xuanwu-device-gateway`
- `xuanwu-iot-gateway`
- `mosquitto`

注意：

- 这套 Compose 启动的是本仓库内的本地平台服务，不包含 `XuanWu` 本体。
- 如果你希望 `Agents`、`AI Config Proxy`、上游智能体管理与执行能力真正可用，还需要一个可访问的 `XuanWu` 服务，并正确设置 `XUANWU_BASE_URL`。

## 适用场景

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
- 一个可选但推荐的 `data/.config.yaml`
- 一个可访问的 `XuanWu` 上游地址

## 第一步：获取源码

```bash
git clone https://github.com/GrissonWu07/xuanwu-ai-platform.git
cd xuanwu-ai-platform
```

如果你不是用 `git clone`，也可以直接下载仓库压缩包。

## 第二步：理解部署锚点目录

当前这套 Docker 全模块部署，是以：

```text
main/xuanwu-device-gateway
```

作为部署锚点目录的。

这是当前代码结构决定的，不是文档额外加的要求：

- `docker-compose_all.yml` 在这里
- `config.yaml` 在这里
- `data/.config.yaml` 从这里读取
- `models/SenseVoiceSmall/model.pt` 从这里挂载

所以接下来的目录准备和启动命令，都会围绕这个目录进行。

如果你需要手动进入部署目录，请进入：

```text
main/xuanwu-device-gateway
```

## 第三步：准备目录和模型

确保以下目录存在：

```text
main/xuanwu-device-gateway
├─ data
├─ models
│  └─ SenseVoiceSmall
│     └─ model.pt
└─ docker-compose_all.yml
```

创建目录：

```bash
mkdir -p main/xuanwu-device-gateway/data
mkdir -p main/xuanwu-device-gateway/models/SenseVoiceSmall
```

下载模型文件并放到：

```text
main/xuanwu-device-gateway/models/SenseVoiceSmall/model.pt
```

可用下载地址：

- [ModelScope - SenseVoiceSmall model.pt](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)

## 第四步：准备配置

当前 `xuanwu-device-gateway` 的配置加载顺序是：

1. `main/xuanwu-device-gateway/config.yaml`
2. `main/xuanwu-device-gateway/data/.config.yaml`
3. 环境变量覆盖

如果你想做本地覆盖，建议把默认配置复制一份：

```bash
cp main/xuanwu-device-gateway/config.yaml main/xuanwu-device-gateway/data/.config.yaml
```

最常见的本地覆盖是：

- `server.websocket`
- `server.http_port`
- `xuanwu-management-server`
- 语音、模型、工具链相关 provider 配置

这个步骤是可选的。

推荐复制一份覆盖配置，而不是直接改默认配置，是因为当前代码会把默认配置和本地覆盖配置合并加载，升级时更容易保留你的本地改动。

如果你只想先把整套平台拉起来做联通验证，`main/xuanwu-device-gateway/data/.config.yaml` 可以先留空文件。

## 第五步：确认上游 `XuanWu` 地址

当前 Compose 默认会让 `xuanwu-management-server` 使用：

```text
XUANWU_BASE_URL=http://xuanwu-ai:8000
```

如果你的 `XuanWu` 不在这个地址，请先改 `docker-compose_all.yml` 里的这两个环境变量：

- `XUANWU_BASE_URL`
- `XUANWU_CONTROL_PLANE_SECRET`

如果暂时没有 `XuanWu`，本地平台层大部分服务仍然可以启动，但以下能力会受影响：

- `Agents` 页面真实数据
- `AI Config Proxy`
- 智能体执行与设备调用闭环

## 第六步：启动全模块

```bash
cd main/xuanwu-device-gateway
docker compose -f docker-compose_all.yml up -d
```

查看容器状态：

```bash
docker compose -f docker-compose_all.yml ps
```

查看关键日志：

```bash
docker logs -f xuanwu-management-server
docker logs -f xuanwu-device-gateway
docker logs -f xuanwu-iot-gateway
docker logs -f xuanwu-jobs
docker logs -f xuanwu-portal
```

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

### 1. 为什么全模块已经启动，但 Agents 页面没有真实数据？

因为当前 Compose 不包含 `XuanWu` 本体。你还需要：

- 单独部署 `XuanWu`
- 把 `XUANWU_BASE_URL` 指向它
- 对齐管理密钥和执行密钥

### 2. 为什么 `xuanwu-device-gateway` 启动失败？

最常见原因是：

- `models/SenseVoiceSmall/model.pt` 不存在
- `data/.config.yaml` 里有错误配置
- 挂载目录权限不正确

### 3. 为什么 `xuanwu-portal` 能打开，但部分页面没有数据？

常见原因有：

- `xuanwu-management-server` 没起来
- `xuanwu-management-server` 没法访问 `XuanWu`
- 还没有真实设备、发现设备或调度记录

## 停止与重启

停止：

```bash
docker compose -f docker-compose_all.yml down
```

重启：

```bash
docker compose -f docker-compose_all.yml up -d
```

强制重建：

```bash
docker compose -f docker-compose_all.yml up -d --build
```

## 相关阅读

- [快速开始](./quick-start.md)
- [平台交付总览](./platform-delivery-overview.md)
- [设备接入与纳管指南](./device-ingress-and-management-guide.md)
