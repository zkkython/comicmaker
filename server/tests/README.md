# 测试说明

## 安装依赖

在运行测试之前，需要先安装测试依赖：

```bash
cd server
pip install -r requirements.txt
```

主要测试依赖包括：
- pytest: 测试框架
- httpx: 异步 HTTP 客户端
- pytest-asyncio: 异步测试支持

## 运行测试

### 方式 1: 使用 pytest 直接运行

```bash
cd server
python -m pytest tests/                    # 运行所有测试
python -m pytest tests/test_materials.py   # 运行指定测试文件
python -m pytest tests/ -v                 # 详细输出
```

### 方式 2: 使用测试脚本

```bash
cd server
python tests/run_tests.py                  # 运行所有测试
python tests/run_tests.py --module materials  # 运行指定模块
python tests/run_tests.py -v                # 详细输出
```

### 方式 3: 使用 Web 界面

1. 启动后端服务：`python server/main.py`
2. 访问 `http://localhost:8080/test-api.html`
3. 在页面上执行测试用例

## 注意事项

1. **测试服务器**: 测试需要后端服务运行在 `http://localhost:8000`
2. **测试数据**: 测试数据存储在独立的测试数据目录中，不会影响生产数据
3. **自动清理**: 每个测试前后会自动清理测试数据

## 常见问题

### 1. `Unknown pytest.mark.asyncio` 警告

**原因**: pytest-asyncio 未安装或未正确配置

**解决**: 
```bash
pip install pytest-asyncio
```

### 2. `cannot collect test class 'TestClient'` 错误

**原因**: 类名以 `Test` 开头，pytest 误认为它是测试类

**解决**: 已重命名为 `APITestClient`，如果仍有问题，检查导入

### 3. 测试连接失败

**原因**: 后端服务未启动

**解决**: 先启动后端服务 `python server/main.py`

