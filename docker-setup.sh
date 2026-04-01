#!/bin/sh

set -eu

PROJECT_ROOT="/opt/xuanwu-ai-platform"
DATA_DIR="$PROJECT_ROOT/deploy/data/device-gateway"
POSTGRES_DATA_DIR="$PROJECT_ROOT/deploy/data/pg"
MODEL_DIR="$PROJECT_ROOT/deploy/models/SenseVoiceSmall"
MODEL_PATH="$MODEL_DIR/model.pt"
COMPOSE_PATH="$PROJECT_ROOT/docker-compose.yml"
CONFIG_PATH="$DATA_DIR/.config.yaml"
ENV_PATH="$PROJECT_ROOT/.env"

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

ensure_git() {
    if command -v git >/dev/null 2>&1; then
        return
    fi
    echo "git was not detected. Please install git first."
    exit 1
}

sync_repo() {
    if [ -d "$PROJECT_ROOT/.git" ]; then
        git -C "$PROJECT_ROOT" fetch --all --prune
        git -C "$PROJECT_ROOT" checkout main
        git -C "$PROJECT_ROOT" pull --ff-only origin main
        return
    fi

    rm -rf "$PROJECT_ROOT"
    git clone https://github.com/GrissonWu07/xuanwu-ai-platform.git "$PROJECT_ROOT"
}

if [ "$(id -u)" -ne 0 ]; then
    echo "Please run this script with root privileges."
    exit 1
fi

ensure_docker
ensure_curl
ensure_git
sync_repo

mkdir -p "$DATA_DIR" "$POSTGRES_DATA_DIR" "$MODEL_DIR"

if [ ! -f "$CONFIG_PATH" ]; then
    : > "$CONFIG_PATH"
fi

if [ ! -f "$ENV_PATH" ] && [ -f "$PROJECT_ROOT/.env.example" ]; then
    cp "$PROJECT_ROOT/.env.example" "$ENV_PATH"
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

You can edit local runtime overrides in:
- $CONFIG_PATH

If needed, update XUANWU_BASE_URL and secrets in:
- $ENV_PATH
EOF
