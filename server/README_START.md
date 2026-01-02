# 启动服务说明

## 方式一：使用命令行启动（推荐）

在 `server` 目录下执行：

```bash
# 方式 1：使用启动脚本（自动检测 CPU 核心数）
./start.sh

# 方式 2：直接使用 uvicorn 命令
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --loop asyncio --limit-concurrency 200

# 方式 3：使用 Python 模块方式
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 方式二：使用 Python 直接运行

在 `server` 目录下执行：

```bash
python main.py
```

注意：使用 `python main.py` 时，代码中已经修改为使用导入字符串 `"main:app"`，可以正常使用多进程模式。

## 参数说明

- `--host 0.0.0.0`: 监听所有网络接口
- `--port 8000`: 服务端口
- `--workers N`: 工作进程数（建议设置为 CPU 核心数）
- `--loop asyncio`: 使用 asyncio 事件循环
- `--limit-concurrency 200`: 限制最大并发连接数

## 开发环境 vs 生产环境

### 开发环境（单进程，支持热重载）
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 生产环境（多进程，高性能）
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --loop asyncio --limit-concurrency 200
```

## 检查服务状态

访问以下地址检查服务是否正常：
- 健康检查：http://localhost:8000/api/health
- API 文档：http://localhost:8000/docs

