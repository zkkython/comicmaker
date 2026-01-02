#!/usr/bin/env python3
"""
ComicMaker 主应用
FastAPI 后端服务
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from api import materials, works, episodes, content, test, tools, tasks, styles

app = FastAPI(title="ComicMaker API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(materials.router, prefix="/api/materials", tags=["materials"])
app.include_router(works.router, prefix="/api/works", tags=["works"])
app.include_router(episodes.router, prefix="/api/episodes", tags=["episodes"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(test.router, prefix="/api/test", tags=["test"])
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(styles.router, prefix="/api/styles", tags=["styles"])

# 静态文件服务（用于提供上传的媒体文件）
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(data_dir, exist_ok=True)
app.mount("/data", StaticFiles(directory=data_dir), name="data")


@app.get("/")
async def root():
    return {"message": "ComicMaker API", "version": "1.0.0"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    import multiprocessing
    
    # 配置 uvicorn 以支持更好的并发
    # workers: 工作进程数，设置为 CPU 核心数
    # loop: 使用 asyncio 事件循环
    # limit_concurrency: 限制并发连接数（可选，默认无限制）
    cpu_count = multiprocessing.cpu_count()
    workers = max(8, cpu_count)  # 至少 2 个进程，最多为 CPU 核心数
    
    # 使用导入字符串而不是直接传递 app 对象，以支持多进程模式
    uvicorn.run(
        "main:app",  # 使用导入字符串格式：模块名:应用变量名
        host="0.0.0.0", 
        port=8000,
        workers=workers,  # 多进程模式，提高并发处理能力
        loop="asyncio",  # 使用 asyncio 事件循环
        limit_concurrency=200  # 限制最大并发连接数为 200（每个进程约 50-100）
    )

