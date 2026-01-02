"""
作品管理 API 测试
"""

import pytest
from tests.utils import APITestClient, get_test_image_path
from tests.fixtures import create_test_work
import os


@pytest.mark.asyncio
async def test_list_works(client: APITestClient):
    """测试列出所有作品"""
    response = await client.get("/api/works")
    assert response.status_code == 200
    data = response.json()
    assert "works" in data
    assert isinstance(data["works"], list)


@pytest.mark.asyncio
async def test_create_work(client: APITestClient):
    """测试创建作品"""
    data = {
        "name": "测试作品",
        "description": "这是一个测试作品"
    }
    response = await client.post("/api/works", data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == "测试作品"
    assert "id" in result
    assert result["default_aspect_ratio"] == "16:9"  # 默认值


@pytest.mark.asyncio
async def test_get_work(client: APITestClient):
    """测试获取作品详情"""
    work_id, _ = create_test_work(name="测试作品")
    
    response = await client.get(f"/api/works/{work_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "测试作品"
    assert data["id"] == work_id


@pytest.mark.asyncio
async def test_update_work(client: APITestClient):
    """测试更新作品"""
    work_id, _ = create_test_work(name="原始名称")
    
    data = {
        "name": "更新后的名称",
        "description": "更新后的描述",
        "style_description": "新的风格描述",
        "default_aspect_ratio": "9:16"
    }
    response = await client.put(f"/api/works/{work_id}", data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == "更新后的名称"
    assert result["default_aspect_ratio"] == "9:16"


@pytest.mark.asyncio
async def test_update_work_invalid_aspect_ratio(client: APITestClient):
    """测试无效的宽高比"""
    work_id, _ = create_test_work()
    
    data = {
        "default_aspect_ratio": "invalid"
    }
    response = await client.put(f"/api/works/{work_id}", data=data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_work(client: APITestClient):
    """测试删除作品"""
    work_id, _ = create_test_work()
    
    response = await client.delete(f"/api/works/{work_id}")
    assert response.status_code == 200
    
    # 验证已删除
    response = await client.get(f"/api/works/{work_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_work(client: APITestClient):
    """测试获取不存在的作品"""
    response = await client.get("/api/works/nonexistent_id")
    assert response.status_code == 404

