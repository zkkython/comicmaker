"""
pytest 配置和共享 fixtures
"""

import pytest
import os
import shutil
import sys
from pathlib import Path
import httpx

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import DATA_ROOT, get_data_path, list_dirs, delete_dir
from tests.utils import APITestClient

# 测试数据目录
TEST_DATA_ROOT = os.path.join(DATA_ROOT, "test_data")


def cleanup_all_test_data():
    """清理所有测试数据"""
    # 清理测试数据目录
    if os.path.exists(TEST_DATA_ROOT):
        shutil.rmtree(TEST_DATA_ROOT)
    
    # 清理主数据目录中的测试数据
    # 通过检查名称中包含"测试"的数据来识别测试数据
    # 注意：此方法假设测试数据名称包含"测试"关键字
    
    import json
    
    # 清理测试作品（名称包含"测试"或"Test"）
    works_path = get_data_path("works")
    if os.path.exists(works_path):
        for work_id in list_dirs(works_path):
            work_meta_path = os.path.join(works_path, work_id, "meta.json")
            if os.path.exists(work_meta_path):
                try:
                    with open(work_meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    name = meta.get("name", "")
                    description = meta.get("description", "")
                    # 如果名称或描述包含"测试"或"Test"，认为是测试数据
                    if ("测试" in name or "Test" in name or "test" in name.lower() or
                        "测试" in description or "Test" in description or "test" in description.lower()):
                        delete_dir(os.path.join(works_path, work_id))
                except Exception:
                    # 如果读取失败，可能是损坏的数据，也删除
                    try:
                        delete_dir(os.path.join(works_path, work_id))
                    except Exception:
                        pass
    
    # 清理测试素材（名称包含"测试"或"Test"）
    for material_type in ["characters", "scenes", "props"]:
        materials_path = get_data_path("materials", material_type)
        if os.path.exists(materials_path):
            for material_id in list_dirs(materials_path):
                material_meta_path = os.path.join(materials_path, material_id, "meta.json")
                if os.path.exists(material_meta_path):
                    try:
                        with open(material_meta_path, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                        name = meta.get("name", "")
                        description = meta.get("description", "")
                        # 如果名称或描述包含"测试"或"Test"，认为是测试数据
                        if ("测试" in name or "Test" in name or "test" in name.lower() or
                            "测试" in description or "Test" in description or "test" in description.lower()):
                            delete_dir(os.path.join(materials_path, material_id))
                    except Exception:
                        # 如果读取失败，可能是损坏的数据，也删除
                        try:
                            delete_dir(os.path.join(materials_path, material_id))
                        except Exception:
                            pass
    
    # 清理测试剧集（在测试作品下的剧集会在作品删除时一起删除，但也要单独检查）
    # 遍历所有作品，清理其中的测试剧集
    if os.path.exists(works_path):
        for work_id in list_dirs(works_path):
            episodes_path = get_data_path("works", work_id, "episodes")
            if os.path.exists(episodes_path):
                for episode_id in list_dirs(episodes_path):
                    episode_meta_path = os.path.join(episodes_path, episode_id, "meta.json")
                    if os.path.exists(episode_meta_path):
                        try:
                            with open(episode_meta_path, "r", encoding="utf-8") as f:
                                meta = json.load(f)
                            name = meta.get("name", "")
                            description = meta.get("description", "")
                            # 如果名称或描述包含"测试"或"Test"，认为是测试数据
                            if ("测试" in name or "Test" in name or "test" in name.lower() or
                                "测试" in description or "Test" in description or "test" in description.lower()):
                                delete_dir(os.path.join(episodes_path, episode_id))
                        except Exception:
                            # 如果读取失败，可能是损坏的数据，也删除
                            try:
                                delete_dir(os.path.join(episodes_path, episode_id))
                            except Exception:
                                pass


@pytest.fixture(scope="function", autouse=True)
def cleanup_test_data():
    """每个测试前后清理测试数据"""
    # 测试前清理
    cleanup_all_test_data()
    
    yield
    
    # 测试后清理
    cleanup_all_test_data()


@pytest.fixture
def test_data_root():
    """返回测试数据根目录"""
    os.makedirs(TEST_DATA_ROOT, exist_ok=True)
    return TEST_DATA_ROOT


@pytest.fixture
async def client():
    """提供测试客户端"""
    test_client = APITestClient()
    yield test_client
    await test_client.close()

