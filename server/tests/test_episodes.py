"""
剧集管理 API 测试
"""

import pytest
from tests.utils import APITestClient
from tests.fixtures import create_test_work, create_test_episode


@pytest.mark.asyncio
async def test_list_episodes(client: APITestClient):
    """测试列出剧集"""
    work_id, _ = create_test_work()
    
    response = await client.get(f"/api/episodes/{work_id}")
    assert response.status_code == 200
    data = response.json()
    assert "episodes" in data
    assert isinstance(data["episodes"], list)


@pytest.mark.asyncio
async def test_create_episode(client: APITestClient):
    """测试创建剧集"""
    work_id, _ = create_test_work()
    
    data = {
        "name": "测试剧集",
        "description": "这是一个测试剧集"
    }
    response = await client.post(f"/api/episodes/{work_id}", data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == "测试剧集"
    assert "id" in result
    assert result["work_id"] == work_id


@pytest.mark.asyncio
async def test_get_episode(client: APITestClient):
    """测试获取剧集详情"""
    work_id, _ = create_test_work()
    episode_id, _ = create_test_episode(work_id, name="测试剧集")
    
    response = await client.get(f"/api/episodes/{work_id}/{episode_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "测试剧集"
    assert data["id"] == episode_id


@pytest.mark.asyncio
async def test_update_episode(client: APITestClient):
    """测试更新剧集"""
    work_id, _ = create_test_work()
    episode_id, _ = create_test_episode(work_id, name="原始名称")
    
    data = {
        "name": "更新后的名称",
        "description": "更新后的描述"
    }
    response = await client.put(f"/api/episodes/{work_id}/{episode_id}", data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == "更新后的名称"


@pytest.mark.asyncio
async def test_delete_episode(client: APITestClient):
    """测试删除剧集"""
    work_id, _ = create_test_work()
    episode_id, _ = create_test_episode(work_id)
    
    response = await client.delete(f"/api/episodes/{work_id}/{episode_id}")
    assert response.status_code == 200
    
    # 验证已删除
    response = await client.get(f"/api/episodes/{work_id}/{episode_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_save_script(client: APITestClient):
    """测试保存脚本"""
    work_id, _ = create_test_work()
    episode_id, _ = create_test_episode(work_id)
    
    data = {
        "script": "这是测试脚本内容",
        "expected_duration": 120.5
    }
    response = await client.put(f"/api/episodes/{work_id}/{episode_id}/script", data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["script"] == "这是测试脚本内容"
    assert result["expected_duration"] == 120.5


@pytest.mark.asyncio
async def test_get_script(client: APITestClient):
    """测试获取脚本"""
    work_id, _ = create_test_work()
    episode_id, _ = create_test_episode(work_id)
    
    # 先保存脚本
    data = {
        "script": "测试脚本",
        "expected_duration": 60.0
    }
    await client.put(f"/api/episodes/{work_id}/{episode_id}/script", data=data)
    
    # 获取脚本
    response = await client.get(f"/api/episodes/{work_id}/{episode_id}/script")
    assert response.status_code == 200
    result = response.json()
    assert result["script"] == "测试脚本"


@pytest.mark.asyncio
async def test_get_storyboard(client: APITestClient):
    """测试获取分镜脚本"""
    work_id, _ = create_test_work()
    episode_id, _ = create_test_episode(work_id)
    
    response = await client.get(f"/api/episodes/{work_id}/{episode_id}/storyboard")
    assert response.status_code == 200
    data = response.json()
    assert "shots" in data

