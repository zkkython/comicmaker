"""
测试工具模块
"""

import httpx
import os
import pytest
from pathlib import Path
from typing import Optional

# 测试服务器地址
TEST_BASE_URL = "http://localhost:8000"


class APITestClient:
    """测试 HTTP 客户端"""
    
    def __init__(self, base_url: str = TEST_BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
    
    async def get(self, path: str, **kwargs):
        """GET 请求"""
        return await self.client.get(path, **kwargs)
    
    async def post(self, path: str, **kwargs):
        """POST 请求"""
        return await self.client.post(path, **kwargs)
    
    async def put(self, path: str, **kwargs):
        """PUT 请求"""
        # 处理文件上传
        if "files" in kwargs and "data" in kwargs:
            files = kwargs.pop("files")
            data = kwargs.pop("data")
            return await self.client.put(path, files=files, data=data, **kwargs)
        return await self.client.put(path, **kwargs)
    
    async def delete(self, path: str, **kwargs):
        """DELETE 请求"""
        return await self.client.delete(path, **kwargs)
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


def create_test_image(file_path: str, size: tuple = (100, 100)):
    """创建测试图片文件"""
    from PIL import Image
    img = Image.new('RGB', size, color='red')
    img.save(file_path, 'JPEG')
    return file_path


def get_test_image_path() -> str:
    """获取测试图片路径（使用简单的占位符）"""
    # 创建一个简单的测试图片
    test_dir = Path(__file__).parent / "fixtures"
    test_dir.mkdir(exist_ok=True)
    test_image_path = test_dir / "test_image.jpg"
    
    # 如果图片不存在，创建一个简单的占位符文件
    if not test_image_path.exists():
        # 创建一个最小的 JPEG 文件（1x1 像素）
        # JPEG 文件头 + 最小图像数据
        jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xaa\xff\xd9'
        test_image_path.write_bytes(jpeg_data)
    
    return str(test_image_path)

