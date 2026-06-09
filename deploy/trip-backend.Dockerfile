FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install \
    --index-url https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    --timeout 120 \
    --retries 10 \
    -r requirements.txt \
    amap-mcp-server==0.1.11

COPY app ./app
COPY run.py ./run.py
RUN sed -i 's/\["uvx", "amap-mcp-server"\]/["amap-mcp-server"]/g' \
    app/agents/trip_planner_agent.py \
    app/services/amap_service.py

EXPOSE 8001

CMD ["python", "run.py"]
