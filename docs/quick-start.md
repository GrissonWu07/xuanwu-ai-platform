# 快速开始

如果你第一次接触这个仓库，推荐直接从仓库根目录启动整套本地平台层。

## 推荐路径

当前 Quick Start 只保留一条推荐路径：

- 全模块 Docker 部署

适合：

- 想先看到 `xuanwu-portal`
- 想验证设备接入、设备管理、Jobs、告警、发现设备纳管
- 想跑起当前仓库里的本地平台主线

详细说明见：

- [部署指南](./Deployment.md)

## 5 分钟启动本地平台层

### 1. 获取源码

```bash
git clone https://github.com/GrissonWu07/xuanwu-ai-platform.git
cd xuanwu-ai-platform
```

### 2. 准备根目录部署目录

当前仓库已经把部署入口提到了仓库根目录。你只需要准备：

```bash
mkdir -p deploy/data
mkdir -p deploy/models/SenseVoiceSmall
```

这两个目录的用途分别是：

- `deploy/data`：本地覆盖配置、运行时落盘数据
- `deploy/models/SenseVoiceSmall`：会话设备网关需要的本地模型文件

### 3. 下载模型文件

下载 `SenseVoiceSmall` 的 `model.pt`，保存到：

```text
deploy/models/SenseVoiceSmall/model.pt
```

下载地址：

- [ModelScope - SenseVoiceSmall model.pt](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)

### 4. 按需准备本地覆盖配置

如果你需要覆盖默认配置，请在根目录创建：

```text
deploy/data/.config.yaml
```

这一步是可选的。

当前设计里：

- 服务默认配置仍然在各自服务目录中维护
- 根目录的 `deploy/data/.config.yaml` 通过 Docker 挂载映射到 `xuanwu-device-gateway`
- 这样你不需要直接修改服务内默认配置文件

如果你只是先把整套平台拉起来做联通验证，`deploy/data/.config.yaml` 可以先留空文件。

### 5. 确认 `XuanWu` 地址

当前根目录 `docker-compose.yml` 默认假设：

```text
XUANWU_BASE_URL=http://xuanwu-ai:8000
```

如果你的 `XuanWu` 不在这个地址，请先修改根目录：

```text
docker-compose.yml
```

### 6. 启动

```bash
docker compose up -d
```

### 7. 验证

打开：

- `http://127.0.0.1:18081` 查看 `xuanwu-portal`

再检查：

```bash
docker compose ps
docker logs -f xuanwu-management-server
docker logs -f xuanwu-device-gateway
docker logs -f xuanwu-iot-gateway
docker logs -f xuanwu-jobs
```

## 默认入口

- `xuanwu-portal`: `http://127.0.0.1:18081`
- `xuanwu-management-server`: `http://127.0.0.1:18082`
- `xuanwu-jobs`: `http://127.0.0.1:18083/jobs/v1/health`
- `xuanwu-iot-gateway`: `http://127.0.0.1:18084/gateway/v1/health`
- `xuanwu-device-gateway` WebSocket: `ws://127.0.0.1:8000/xuanwu/v1/`
- `xuanwu-device-gateway` OTA: `http://127.0.0.1:8003/xuanwu/ota/`

## 接下来建议阅读

- [部署指南](./Deployment.md)
- [当前平台能力说明](./current-platform-capabilities.md)
- [当前 API 总览](./current-api-surfaces.md)
- [设备接入与纳管指南](./device-ingress-and-management-guide.md)
