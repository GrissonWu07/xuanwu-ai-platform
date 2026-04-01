# 快速开始

如果你第一次接触这个仓库，推荐从这里开始。

## 你应该先选哪条路径

### 路径 A：全模块 Docker 部署，推荐

适合：

- 想先看到 `xuanwu-portal`
- 想验证设备接入、设备管理、Jobs、告警、发现设备纳管
- 想跑起当前仓库里的本地平台主线

入口文档：

- [全模块部署指南](./Deployment_all.md)

### 路径 B：最简部署

适合：

- 只想先启动 `xuanwu-device-gateway`
- 只验证会话型设备接入
- 暂时不需要 portal、management、iot-gateway、jobs

入口文档：

- [最简部署指南](./Deployment.md)

## 推荐路径：5 分钟启动本地平台层

### 1. 获取源码

```bash
git clone https://github.com/GrissonWu07/xuanwu-ai-platform.git
cd xuanwu-ai-platform/main/xuanwu-device-gateway
```

### 2. 准备目录

```bash
mkdir -p data models/SenseVoiceSmall
```

### 3. 下载模型文件

下载 `SenseVoiceSmall` 的 `model.pt` 并保存到：

```text
main/xuanwu-device-gateway/models/SenseVoiceSmall/model.pt
```

下载地址：

- [ModelScope - SenseVoiceSmall model.pt](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)

### 4. 按需准备本地覆盖配置

如果你需要覆盖默认配置：

```bash
cp config.yaml data/.config.yaml
```

如果只是先拉起整套平台做联通验证，`data/.config.yaml` 可以先保留为空文件。

### 5. 确认 `XuanWu` 地址

当前全模块 Compose 默认假设：

```text
XUANWU_BASE_URL=http://xuanwu-ai:8000
```

如果你的 `XuanWu` 不在这个地址，请先修改：

```text
main/xuanwu-device-gateway/docker-compose_all.yml
```

### 6. 启动

```bash
docker compose -f docker-compose_all.yml up -d
```

### 7. 验证

打开：

- `http://127.0.0.1:18081` 查看 `xuanwu-portal`

再检查：

```bash
docker compose -f docker-compose_all.yml ps
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

## 你接下来应该看什么

- 想看部署细节：看 [全模块部署指南](./Deployment_all.md)
- 想只跑设备接入：看 [最简部署指南](./Deployment.md)
- 想看平台能力：看 [当前平台能力说明](./current-platform-capabilities.md)
- 想看 API：看 [当前 API 总览](./current-api-surfaces.md)
- 想理解设备纳管：看 [设备接入与纳管指南](./device-ingress-and-management-guide.md)
