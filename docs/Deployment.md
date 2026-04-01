# 最简部署指南

本文档描述当前仓库里最轻量的部署路径：只运行 `xuanwu-device-gateway`。

这条路径适合：

- 只验证会话型设备接入
- 只需要 WebSocket、OTA、Vision 相关入口
- 不需要统一门户、统一管理面、统一任务调度

如果你需要完整的本地平台，请看 [全模块部署指南](./Deployment_all.md)。

## 会启动什么

最简部署只启动：

- `xuanwu-device-gateway`

它不会启动：

- `xuanwu-portal`
- `xuanwu-management-server`
- `xuanwu-iot-gateway`
- `xuanwu-jobs`

## 部署前准备

你需要准备：

- Docker 和 Docker Compose Plugin
- 本仓库源码
- `SenseVoiceSmall` 的 `model.pt`
- 可选的 `data/.config.yaml`

## 第一步：获取源码

```bash
git clone https://github.com/GrissonWu07/xuanwu-ai-platform.git
cd xuanwu-ai-platform/main/xuanwu-device-gateway
```

## 第二步：准备目录和模型

创建目录：

```bash
mkdir -p data models/SenseVoiceSmall
```

下载模型文件并保存到：

```text
main/xuanwu-device-gateway/models/SenseVoiceSmall/model.pt
```

可用下载地址：

- [ModelScope - SenseVoiceSmall model.pt](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)

## 第三步：准备配置

当前配置加载顺序是：

1. `config.yaml`
2. `data/.config.yaml`
3. 环境变量覆盖

如果你需要自定义配置，推荐：

```bash
cp config.yaml data/.config.yaml
```

然后只在 `data/.config.yaml` 里覆盖你关心的字段。

如果只是先启动测试，也可以让 `data/.config.yaml` 保持为空文件：

```bash
type nul > data\\.config.yaml
```

如果你在 Linux/macOS：

```bash
touch data/.config.yaml
```

## 第四步：启动服务

```bash
docker compose up -d
```

查看容器：

```bash
docker compose ps
```

查看日志：

```bash
docker logs -f xuanwu-device-gateway
```

## 默认端口

最简部署会暴露：

- WebSocket: `ws://127.0.0.1:8000/xuanwu/v1/`
- OTA: `http://127.0.0.1:8003/xuanwu/ota/`
- Vision: `http://127.0.0.1:8003/mcp/vision/explain`

## 如何验证

启动后，至少确认以下两点：

1. `docker compose ps` 里 `xuanwu-device-gateway` 处于运行状态
2. 日志里没有模型文件缺失、配置文件解析失败、端口绑定失败

## 常见问题

### 1. 为什么容器直接退出？

常见原因：

- 没有 `models/SenseVoiceSmall/model.pt`
- `data/.config.yaml` 配置非法
- 端口 `8000` 或 `8003` 被占用

### 2. 什么时候不该用最简部署？

这些场景不建议用最简部署：

- 需要统一设备管理
- 需要 `xuanwu-portal`
- 需要 IoT/工业设备协议接入
- 需要 jobs 调度
- 需要统一遥测、事件、告警与发现设备纳管

## 停止与重启

停止：

```bash
docker compose down
```

重启：

```bash
docker compose up -d
```

## 相关阅读

- [快速开始](./quick-start.md)
- [全模块部署指南](./Deployment_all.md)
- [设备接入与纳管指南](./device-ingress-and-management-guide.md)
