FROM python:3.11-slim

WORKDIR /opt/xuanwu-jobs

COPY main/xuanwu-jobs /opt/xuanwu-jobs

RUN pip install --no-cache-dir aiohttp pyyaml httpx

CMD ["python", "app.py"]
