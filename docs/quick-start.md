# 快速开始

如果你第一次接触这个仓库，推荐直接从仓库根目录启动整套本地平台层。

## 推荐路径

当前 Quick Start 只保留一条推荐路径：

- 全模块 Docker 部署

## 默认持久化

当前根目录部署默认会一起启动 PostgreSQL，并作为平台主持久化层：

- `xuanwu-management-server` 使用 schema `xw_mgmt`
- `xuanwu-iot-gateway` 使用 schema `xw_iot`
- PostgreSQL 宿主机数据目录为 `deploy/data/pg`

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
mkdir -p deploy/data/device-gateway
mkdir -p deploy/data/pg
mkdir -p deploy/models/SenseVoiceSmall
```

这两个目录的用途分别是：

- `deploy/data/device-gateway`：`xuanwu-device-gateway` 的本地覆盖配置和运行时落盘数据
- `deploy/data/pg`：PostgreSQL 的宿主机数据目录
- `deploy/models/SenseVoiceSmall`：会话设备网关需要的本地模型文件

### 3. 下载模型文件

当前仓库里已经自带了 `SenseVoiceSmall` 的辅助配置文件：

- `main/xuanwu-device-gateway/models/SenseVoiceSmall/config.yaml`
- `main/xuanwu-device-gateway/models/SenseVoiceSmall/configuration.json`

本地部署时还缺的只有模型权重文件：

```text
deploy/models/SenseVoiceSmall/model.pt
```

推荐下载方案如下。

国内网络优先，推荐使用 ModelScope：

```bash
python -m pip install -U modelscope
python -m modelscope.cli download --model iic/SenseVoiceSmall --file model.pt --local_dir deploy/models/SenseVoiceSmall
```

官方页面：

- [ModelScope - iic/SenseVoiceSmall](https://modelscope.cn/models/iic/SenseVoiceSmall)

如果你所在环境访问 Hugging Face 更稳定，也可以直接下载：

```bash
curl -L "https://huggingface.co/FunAudioLLM/SenseVoiceSmall/resolve/main/model.pt" -o deploy/models/SenseVoiceSmall/model.pt
```

官方页面：

- [Hugging Face - FunAudioLLM/SenseVoiceSmall](https://huggingface.co/FunAudioLLM/SenseVoiceSmall)

下载完成后，请确认文件存在：

```bash
ls -lh deploy/models/SenseVoiceSmall/model.pt
```

### 4. 准备根目录环境配置

根目录部署现在推荐通过：

```text
.env
```

管理上游地址和部署密钥。

第一次启动前，先复制：

```bash
cp .env.example .env
```

至少确认：

```text
XUANWU_BASE_URL=http://你的-xuanwu-地址
```

### 5. 按需准备本地覆盖配置

如果你需要覆盖默认配置，请在根目录创建：

```text
deploy/data/device-gateway/.config.yaml
```

这一步是可选的。

当前设计里：

- 服务默认配置仍然在各自服务目录中维护
- 根目录的 `deploy/data/device-gateway/.config.yaml` 会映射到容器内 `data/.config.yaml`
- 这样你不需要直接修改服务内默认配置文件
- `xuanwu-device-gateway` 产生的本地短期记忆也会落到宿主机：
  - `deploy/data/device-gateway/.memory.yaml`

如果你只是先把整套平台拉起来做联通验证，`deploy/data/device-gateway/.config.yaml` 可以先留空文件。

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
