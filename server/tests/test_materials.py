"""
素材管理 API 测试
"""

import pytest
from tests.utils import APITestClient, get_test_image_path
from tests.fixtures import create_test_material
import os


@pytest.mark.asyncio
async def test_list_materials_characters(client: APITestClient):
    """测试列出人物角色"""
    response = await client.get("/api/materials/characters")
    assert response.status_code == 200
    data = response.json()
    assert "materials" in data
    assert isinstance(data["materials"], list)


@pytest.mark.asyncio
async def test_list_materials_scenes(client: APITestClient):
    """测试列出场景"""
    response = await client.get("/api/materials/scenes")
    assert response.status_code == 200
    data = response.json()
    assert "materials" in data


@pytest.mark.asyncio
async def test_list_materials_props(client: APITestClient):
    """测试列出道具"""
    response = await client.get("/api/materials/props")
    assert response.status_code == 200
    data = response.json()
    assert "materials" in data


@pytest.mark.asyncio
async def test_create_character(client: APITestClient):
    """测试创建人物角色"""
    image_path = get_test_image_path()
    
    with open(image_path, "rb") as f:
        files = {"main_image": ("test.jpg", f.read(), "image/jpeg")}
        data = {
            "name": "测试角色",
            "description": "这是一个测试角色"
        }
        response = await client.post("/api/materials/characters", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == "测试角色"
    assert result["description"] == "这是一个测试角色"
    assert "id" in result


@pytest.mark.asyncio
async def test_get_character(client: APITestClient):
    """测试获取人物角色"""
    # 先创建一个角色
    image_path = get_test_image_path()
    material_id, _ = create_test_material("characters", name="测试角色")
    
    response = await client.get(f"/api/materials/characters/{material_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "测试角色"


@pytest.mark.asyncio
async def test_update_character(client: APITestClient):
    """测试更新人物角色"""
    material_id, _ = create_test_material("characters", name="原始名称")
    
    data = {
        "name": "更新后的名称",
        "description": "更新后的描述"
    }
    response = await client.put(f"/api/materials/characters/{material_id}", data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == "更新后的名称"


@pytest.mark.asyncio
async def test_delete_character(client: APITestClient):
    """测试删除人物角色"""
    material_id, _ = create_test_material("characters")
    
    response = await client.delete(f"/api/materials/characters/{material_id}")
    assert response.status_code == 200
    
    # 验证已删除
    response = await client.get(f"/api/materials/characters/{material_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_material_type(client: APITestClient):
    """测试无效的素材类型"""
    response = await client.get("/api/materials/invalid_type")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_nonexistent_material(client: APITestClient):
    """测试获取不存在的素材"""
    response = await client.get("/api/materials/characters/nonexistent_id")
    assert response.status_code == 404

