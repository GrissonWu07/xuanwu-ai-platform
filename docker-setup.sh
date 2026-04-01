#!/bin/sh

set -eu

PROJECT_ROOT="/opt/xuanwu-device-gateway"
DATA_DIR="$PROJECT_ROOT/data"
MODEL_DIR="$PROJECT_ROOT/models/SenseVoiceSmall"
MODEL_PATH="$MODEL_DIR/model.pt"
COMPOSE_PATH="$PROJECT_ROOT/docker-compose_all.yml"
CONFIG_PATH="$DATA_DIR/.config.yaml"

download_if_missing() {
    filepath=$1
    url=$2
    if [ -f "$filepath" ]; then
        echo "$filepath already exists, skipping download"
        return
    fi
    curl -fL --progress-bar "$url" -o "$filepath"
}

ensure_docker() {
    if command -v docker >/dev/null 2>&1; then
        return
    fi
    echo "Docker was not detected. Please install Docker first."
    exit 1
}

ensure_curl() {
    if command -v curl >/dev/null 2>&1; then
        return
    fi
    echo "curl was not detected. Please install curl first."
    exit 1
}

if [ "$(id -u)" -ne 0 ]; then
    echo "Please run this script with root privileges."
    exit 1
fi

ensure_docker
ensure_curl

mkdir -p "$DATA_DIR" "$MODEL_DIR"

download_if_missing \
    "$COMPOSE_PATH" \
    "https://ghfast.top/https://raw.githubusercontent.com/GrissonWu07/ai-assist-deviceserver/refs/heads/main/main/xuanwu-device-gateway/docker-compose_all.yml"

if [ ! -f "$CONFIG_PATH" ]; then
    : > "$CONFIG_PATH"
fi

download_if_missing \
    "$MODEL_PATH" \
    "https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt"

docker compose -f "$COMPOSE_PATH" up -d

LOCAL_IP=$(hostname -I | awk '{print $1}')

cat <<EOF

XuanWu AI Python stack is up:

- unified portal xuanwu-portal: http://$LOCAL_IP:18081
- management host xuanwu-management-server: http://$LOCAL_IP:18082
- gateway host xuanwu-iot-gateway: http://$LOCAL_IP:18084/gateway/v1/health
- jobs scheduler-dispatcher xuanwu-jobs: http://$LOCAL_IP:18083/jobs/v1/health
- OTA endpoint: http://$LOCAL_IP:8003/xuanwu/ota/
- vision endpoint: http://$LOCAL_IP:8003/mcp/vision/explain
- WebSocket endpoint: ws://$LOCAL_IP:8000/xuanwu/v1/

Please make sure the external XuanWu service is reachable through XUANWU_BASE_URL.
EOF
