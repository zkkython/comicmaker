#!/bin/bash
# 启动 ComicMaker 后端服务

# 进入 server 目录
cd "$(dirname "$0")"

# 获取 CPU 核心数
CPU_COUNT=$(python3 -c "import multiprocessing; print(max(2, multiprocessing.cpu_count()))")

echo "启动 ComicMaker 后端服务..."
echo "CPU 核心数: $CPU_COUNT"
echo "工作进程数: $CPU_COUNT"
echo "监听地址: 0.0.0.0:8000"
echo ""

# 使用 uvicorn 命令行启动（推荐方式）
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers $CPU_COUNT \
    --loop asyncio \
    --limit-concurrency 200

