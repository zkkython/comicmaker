"""
内容生成 API 测试
"""

import pytest
from tests.utils import APITestClient
from tests.fixtures import create_test_work, create_test_episode
from utils import get_data_path, save_json, generate_id, ensure_dir
import os


@pytest.mark.asyncio
async def test_generate_storyboard(client: APITestClient):
    """测试生成分镜脚本"""
    work_id, _ = create_test_work()
    episode_id, _ = create_test_episode(work_id)
    
    data = {
        "script": "第一段内容\n\n第二段内容\n\n第三段内容"
    }
    response = await client.post(f"/api/content/{work_id}/{episode_id}/generate-storyboard", data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert "shots" in result
    assert len(result["shots"]) > 0


@pytest.mark.asyncio
async def test_generate_images(client: APITestClient):
    """测试生成图片"""
    work_id, _ = create_test_work()
    episode_id, _ = create_test_episode(work_id)
    shot_id = generate_id()
    
    # 创建分镜目录
    shot_path = get_data_path("works", work_id, "episodes", episode_id, "shots", shot_id)
    ensure_dir(shot_path)
    
    data = {
        "prompt": "测试图片提示词"
    }
    response = await client.post(f"/api/content/{work_id}/{episode_id}/{shot_id}/generate-images", data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert "candidates" in result


@pytest.mark.asyncio
async def test_select_image(client: APITestClient):
    """测试选择图片"""
    work_id, _ = create_test_work()
    episode_id, _ = create_test_episode(work_id)
    shot_id = generate_id()
    
    # 创建分镜目录和元数据
    shot_path = get_data_path("works", work_id, "episodes", episode_id, "shots", shot_id)
    ensure_dir(shot_path)
    images_dir = os.path.join(shot_path, "images")
    ensure_dir(images_dir)
    
    data = {
        "image_path": "images/candidate_1.jpg"
    }
    response = await client.post(f"/api/content/{work_id}/{episode_id}/{shot_id}/select-image", data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["image_path"] == "images/candidate_1.jpg"


@pytest.mark.asyncio
async def test_generate_video(client: APITestClient):
    """测试生成视频"""
    work_id, _ = create_test_work()
    episode_id, _ = create_test_episode(work_id)
    shot_id = generate_id()
    
    # 创建分镜目录
    shot_path = get_data_path("works", work_id, "episodes", episode_id, "shots", shot_id)
    ensure_dir(shot_path)
    
    data = {
        "prompt": "测试视频提示词"
    }
    response = await client.post(f"/api/content/{work_id}/{episode_id}/{shot_id}/generate-video", data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert "video_path" in result


@pytest.mark.asyncio
async def test_generate_audio(client: APITestClient):
    """测试生成音频"""
    work_id, _ = create_test_work()
    episode_id, _ = create_test_episode(work_id)
    shot_id = generate_id()
    
    # 创建分镜目录
    shot_path = get_data_path("works", work_id, "episodes", episode_id, "shots", shot_id)
    ensure_dir(shot_path)
    
    data = {
        "prompt": "测试音频提示词"
    }
    response = await client.post(f"/api/content/{work_id}/{episode_id}/{shot_id}/generate-audio", data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert "audio_path" in result


@pytest.mark.asyncio
async def test_get_shot(client: APITestClient):
    """测试获取分镜详情"""
    work_id, _ = create_test_work()
    episode_id, _ = create_test_episode(work_id)
    shot_id = generate_id()
    
    # 创建分镜目录和元数据
    shot_path = get_data_path("works", work_id, "episodes", episode_id, "shots", shot_id)
    ensure_dir(shot_path)
    meta = {
        "image_prompt": "测试图片提示词",
        "video_prompt": "测试视频提示词",
        "audio_prompt": "测试音频提示词"
    }
    save_json(os.path.join(shot_path, "meta.json"), meta)
    
    response = await client.get(f"/api/content/{work_id}/{episode_id}/{shot_id}")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == shot_id


@pytest.mark.asyncio
async def test_update_prompts(client: APITestClient):
    """测试更新提示词"""
    work_id, _ = create_test_work()
    episode_id, _ = create_test_episode(work_id)
    shot_id = generate_id()
    
    # 创建分镜目录
    shot_path = get_data_path("works", work_id, "episodes", episode_id, "shots", shot_id)
    ensure_dir(shot_path)
    
    data = {
        "image_prompt": "新的图片提示词",
        "video_prompt": "新的视频提示词",
        "audio_prompt": "新的音频提示词"
    }
    response = await client.put(f"/api/content/{work_id}/{episode_id}/{shot_id}/prompts", data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["image_prompt"] == "新的图片提示词"

