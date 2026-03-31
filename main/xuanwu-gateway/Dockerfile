FROM python:3.11-slim

WORKDIR /opt/xuanwu-gateway

COPY main/xuanwu-gateway/requirements.txt /tmp/xuanwu-gateway-requirements.txt
RUN pip install --no-cache-dir -r /tmp/xuanwu-gateway-requirements.txt

COPY main/xuanwu-gateway /opt/xuanwu-gateway

CMD ["python", "app.py"]
