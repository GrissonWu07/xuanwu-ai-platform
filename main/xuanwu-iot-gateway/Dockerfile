FROM python:3.11-slim

WORKDIR /opt/xuanwu-iot-gateway

COPY main/xuanwu-iot-gateway/requirements.txt /tmp/xuanwu-iot-gateway-requirements.txt
RUN pip install --no-cache-dir -r /tmp/xuanwu-iot-gateway-requirements.txt

COPY main/xuanwu-iot-gateway /opt/xuanwu-iot-gateway

CMD ["python", "app.py"]
