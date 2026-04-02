FROM python:3.11-slim

WORKDIR /opt/xuanwu-management-server

COPY main/xuanwu-management-server /opt/xuanwu-management-server

RUN pip install --no-cache-dir aiohttp pyyaml httpx sqlalchemy psycopg[binary]

CMD ["python", "app.py"]
