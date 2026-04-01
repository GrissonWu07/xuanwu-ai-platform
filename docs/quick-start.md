# 快速开始

如果你第一次接触这个仓库，推荐从这里开始。

## 推荐路径

当前 Quick Start 只保留一条推荐路径：

- 全模块 Docker 部署

适合：

- 想先看到 `xuanwu-portal`
- 想验证设备接入、设备管理、Jobs、告警、发现设备纳管
- 想跑起当前仓库里的本地平台主线

入口文档：

- [部署指南](./Deployment.md)

## 推荐路径：5 分钟启动本地平台层

### 1. 获取源码

```bash
git clone https://github.com/GrissonWu07/xuanwu-ai-platform.git
cd xuanwu-ai-platform
```

### 2. 先理解部署锚点目录

当前代码里，`xuanwu-device-gateway` 自己就是部署锚点目录。

原因不是文档约定，而是代码就是这样组织的：

- `docker-compose_all.yml` 在 `main/xuanwu-device-gateway`
- 默认配置文件是 `main/xuanwu-device-gateway/config.yaml`
- 本地覆盖配置是 `main/xuanwu-device-gateway/data/.config.yaml`
- 模型挂载路径是 `main/xuanwu-device-gateway/models/SenseVoiceSmall/model.pt`

也就是说，当前部署路径之所以看起来“怪”，是因为这套本地平台 Docker 入口本来就挂在：

```text
main/xuanwu-device-gateway
```

### 3. 准备目录

```bash
mkdir -p main/xuanwu-device-gateway/data
mkdir -p main/xuanwu-device-gateway/models/SenseVoiceSmall
```

### 4. 下载模型文件

下载 `SenseVoiceSmall` 的 `model.pt` 并保存到：

```text
main/xuanwu-device-gateway/models/SenseVoiceSmall/model.pt
```

下载地址：

- [ModelScope - SenseVoiceSmall model.pt](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)

### 5. 按需准备本地覆盖配置

如果你需要覆盖默认配置：

```bash
cp main/xuanwu-device-gateway/config.yaml main/xuanwu-device-gateway/data/.config.yaml
```

这个步骤是可选的。

之所以推荐这样做，是因为当前代码会把：

- `config.yaml` 作为默认配置
- `data/.config.yaml` 作为本地覆盖配置

两者合并后再启动。这样你不需要直接改默认配置文件，后续升级也更稳。

如果只是先拉起整套平台做联通验证，`main/xuanwu-device-gateway/data/.config.yaml` 可以先保留为空文件。

### 6. 确认 `XuanWu` 地址

当前全模块 Compose 默认假设：

```text
XUANWU_BASE_URL=http://xuanwu-ai:8000
```

如果你的 `XuanWu` 不在这个地址，请先修改：

```text
main/xuanwu-device-gateway/docker-compose_all.yml
```

### 7. 启动

```bash
cd main/xuanwu-device-gateway
docker compose -f docker-compose_all.yml up -d
```

### 8. 验证

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

- 想看部署细节：看 [部署指南](./Deployment.md)
- 想看平台能力：看 [当前平台能力说明](./current-platform-capabilities.md)
- 想看 API：看 [当前 API 总览](./current-api-surfaces.md)
- 想理解设备纳管：看 [设备接入与纳管指南](./device-ingress-and-management-guide.md)
