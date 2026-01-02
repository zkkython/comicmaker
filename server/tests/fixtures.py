"""
测试数据 fixtures
"""

import os
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import get_data_path, save_json, generate_id, ensure_dir


def create_test_work(work_id: str = None, name: str = "测试作品", description: str = "测试描述"):
    """创建测试作品"""
    if work_id is None:
        work_id = generate_id()
    
    work_path = get_data_path("works", work_id)
    ensure_dir(work_path)
    
    meta = {
        "name": name,
        "description": description,
        "cover_images": [],
        "style_description": "测试风格",
        "default_aspect_ratio": "16:9"
    }
    
    meta_path = os.path.join(work_path, "meta.json")
    save_json(meta_path, meta)
    
    return work_id, meta


def create_test_episode(work_id: str, episode_id: str = None, name: str = "测试剧集", description: str = "测试描述"):
    """创建测试剧集"""
    if episode_id is None:
        episode_id = generate_id()
    
    episode_path = get_data_path("works", work_id, "episodes", episode_id)
    ensure_dir(episode_path)
    
    meta = {
        "name": name,
        "description": description,
        "cover_image": None
    }
    
    meta_path = os.path.join(episode_path, "meta.json")
    save_json(meta_path, meta)
    
    return episode_id, meta


def create_test_material(material_type: str, material_id: str = None, name: str = "测试素材", description: str = "测试描述"):
    """创建测试素材"""
    if material_id is None:
        material_id = generate_id()
    
    material_path = get_data_path("materials", material_type, material_id)
    ensure_dir(material_path)
    
    meta = {
        "name": name,
        "description": description,
        "main_image": "main.jpg",
        "aux_images": [],
        "voice_settings": None
    }
    
    meta_path = os.path.join(material_path, "meta.json")
    save_json(meta_path, meta)
    
    # 创建占位图片文件
    main_image_path = os.path.join(material_path, "main.jpg")
    if not os.path.exists(main_image_path):
        with open(main_image_path, "wb") as f:
            f.write(b'fake image data')
    
    return material_id, meta

