FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libopus0 ffmpeg locales && \
    sed -i '/zh_CN.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV LANG=zh_CN.UTF-8 \
    LC_ALL=zh_CN.UTF-8 \
    LANGUAGE=zh_CN:zh \
    PYTHONIOENCODING=utf-8

WORKDIR /opt/xuanwu-device-gateway

COPY main/xuanwu-device-gateway/requirements.txt /opt/xuanwu-device-gateway/requirements.txt

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY main/xuanwu-device-gateway /opt/xuanwu-device-gateway

CMD ["python", "app.py"]
