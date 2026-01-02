#!/usr/bin/env python3
"""
工具函数
"""

import os
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any


# 数据根目录
DATA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def get_data_path(*parts: str) -> str:
    """获取数据路径"""
    return os.path.join(DATA_ROOT, *parts)


def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """加载 JSON 文件"""
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_json(file_path: str, data: Dict[str, Any]):
    """保存 JSON 文件"""
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_id() -> str:
    """生成唯一 ID"""
    return str(uuid.uuid4())


def list_dirs(base_path: str) -> list:
    """列出目录下的所有子目录"""
    if not os.path.exists(base_path):
        return []
    return [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]


def delete_dir(dir_path: str):
    """删除目录及其所有内容"""
    import shutil
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

