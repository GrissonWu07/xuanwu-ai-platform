#!/bin/sh

set -eu

PROJECT_ROOT="/opt/xuanwu-device-server"
DATA_DIR="$PROJECT_ROOT/data"
MODEL_DIR="$PROJECT_ROOT/models/SenseVoiceSmall"
MODEL_PATH="$MODEL_DIR/model.pt"
COMPOSE_PATH="$PROJECT_ROOT/docker-compose_all.yml"
CONFIG_PATH="$DATA_DIR/.config.yaml"

download_if_missing() {
    filepath=$1
    url=$2
    if [ -f "$filepath" ]; then
        echo "$filepath 已存在，跳过下载"
        return
    fi
    curl -fL --progress-bar "$url" -o "$filepath"
}

ensure_docker() {
    if command -v docker >/dev/null 2>&1; then
        return
    fi
    echo "未检测到 Docker，请先安装 Docker 后重新执行本脚本。"
    exit 1
}

ensure_curl() {
    if command -v curl >/dev/null 2>&1; then
        return
    fi
    echo "未检测到 curl，请先安装 curl 后重新执行本脚本。"
    exit 1
}

if [ "$(id -u)" -ne 0 ]; then
    echo "请使用 root 权限运行本脚本。"
    exit 1
fi

ensure_docker
ensure_curl

mkdir -p "$DATA_DIR" "$MODEL_DIR"

download_if_missing \
    "$COMPOSE_PATH" \
    "https://ghfast.top/https://raw.githubusercontent.com/GrissonWu07/ai-assist-deviceserver/refs/heads/main/main/xuanwu-device-server/docker-compose_all.yml"

if [ ! -f "$CONFIG_PATH" ]; then
    : > "$CONFIG_PATH"
fi

download_if_missing \
    "$MODEL_PATH" \
    "https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt"

docker compose -f "$COMPOSE_PATH" up -d

LOCAL_IP=$(hostname -I | awk '{print $1}')

cat <<EOF

玄武AI Python 管理路径已启动：

- 管理宿主 xuanwu-management-server: http://$LOCAL_IP:18082
- OTA 地址: http://$LOCAL_IP:8003/xiaozhi/ota/
- 视觉分析接口: http://$LOCAL_IP:8003/mcp/vision/explain
- WebSocket 地址: ws://$LOCAL_IP:8000/xiaozhi/v1/

请确认外部 XuanWu 服务可通过 docker-compose 中的 XUANWU_BASE_URL 访问。
EOF
